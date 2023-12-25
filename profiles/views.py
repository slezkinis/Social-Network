from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from posts.forms import CommentCreateModelForm
from posts.models import Post
from posts.views_utils import add_comment_if_submitted

from .forms import MessageModelForm
from .models import Message, Profile, Relationship
from .views_utils import (
    check_if_friends,
    follow_unfollow,
    get_friends_of_user,
    get_profile_by_pk,
    get_profile_form_by_request_method,
    get_received_invites,
    get_received_messages,
    get_relationship_users,
    get_request_user_profile,
    get_sent_invites,
    redirect_back,
)
from django.contrib.auth.mixins import AccessMixin

# Function-based views


class VerificateRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.profile.is_verificated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/')
def my_profile_view(request):
    """
    Shows request's user profile.
    View url: /profiles/myprofile/
    """
    profile = get_request_user_profile(request.user)

    form = get_profile_form_by_request_method(request, profile)

    posts = profile.posts.all()

    c_form = CommentCreateModelForm()

    if add_comment_if_submitted(request, profile):
        return redirect_back(request)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.add_message(
            request,
            messages.SUCCESS,
            "Профиль изменён!",
        )

        return redirect_back(request)

    context = {
        "profile": profile,
        "form": form,
        "posts": posts,
        "c_form": c_form,
        "name": request.user,
        "avatar": request.user.profile.avatar.url
    }

    return render(request, "profiles/my_profile.html", context)


# @login_required
def received_invites_view(request):
    """
    Shows request's user received invites.
    View url: /profiles/received_invites/
    """
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.profile.is_verificated:
        return redirect('verificate')
    user = request.user
    profile = get_request_user_profile(user)
    profiles = get_received_invites(profile)

    context = {
        "profiles": profiles,
        'avatar': request.build_absolute_uri(f'/media/{user.profile.avatar}'),
        'name': user.username,
    }

    return render(request, "profiles/received_invites.html", context)


def sent_invites_view(request):
    """
    Shows request's user sent invites.
    View url: /profiles/sent_invites/
    """
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.profile.is_verificated:
        return redirect('verificate')
    user = request.user
    profile = get_request_user_profile(request.user)
    profiles = get_sent_invites(profile)
    context = {
        "profiles": profiles,
        'avatar': request.build_absolute_uri(f'/media/{user.profile.avatar}'),
        'name': user.username,
    }

    return render(request, "profiles/sent_invites.html", context)


@login_required(login_url='/')
def switch_follow(request):
    """
    Follows/unfollows user by pk.
    View url: /profiles/switch_follow/
    """
    if request.method == "POST":
        my_profile = get_request_user_profile(request.user)
        profile = get_profile_by_pk(request)

        follow_unfollow(my_profile, profile)

    return redirect_back(request)


@login_required(login_url='/')
def accept_invitation(request):
    """
    Accepts invitation from user by pk.
    View url: /profiles/received_invites/accept/
    """
    if request.method == "POST":
        sender = get_profile_by_pk(request)
        receiver = get_request_user_profile(request.user)

        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)

        if rel.status == "sent":
            rel.status = "accepted"
            rel.save()

    return redirect_back(request)


@login_required(login_url='/')
def reject_invitation(request):
    """
    Rejects (deletes) invitation from user by pk.
    View url: /profiles/received_invites/reject/
    """
    if request.method == "POST":
        sender = get_profile_by_pk(request)
        receiver = get_request_user_profile(request.user)

        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)

        if rel.status == "sent":
            rel.delete()

    return redirect_back(request)


@login_required(login_url='/')
def my_friends_view(request):
    """
    Shows request's user friends.
    View url: /profiles/my_friends/
    """
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.profile.is_verificated:
        return redirect('verificate')
    user = request.user
    profile = get_request_user_profile(request.user)
    following = profile.following.all()

    profiles = Profile.objects.get_my_friends_profiles(request.user)
    invited_users, incoming_invite_users = get_relationship_users(request.user.profile)
    context = {
        "following": following,
        "profiles": profiles,
        'avatar': request.build_absolute_uri(f'/media/{user.profile.avatar}'),
        'name': user.username,
        "invited_users": invited_users,
        "incoming_invite_users": incoming_invite_users
    }

    return render(request, "profiles/my_friends.html", context)


@login_required(login_url='/')
def search_profiles(request):
    """
    Searches for profiles by their username.
    View url: /profiles/search/
    """
    search = request.GET.get("q", "")
    profiles = Profile.objects.filter(user__username__icontains=search)
    following = request.user.profile.following.all()
    invited_users, incoming_invite_users = get_relationship_users(request.user.profile)
    context = {
        "search": search,
        "profiles": profiles,
        "following": following,
        "invited_users": invited_users,
        "incoming_invite_users": incoming_invite_users,
        "name": request.user,
        "avatar": request.user.profile.avatar.url

    }

    if search:
        return render(request, "profiles/search_profiles.html", context)

    return render(request, "profiles/search_profiles.html")


@login_required(login_url='/')
def send_invitation(request):
    """
    Creates a "sent" relationship between request's profile
    and target profile.
    View url: /profiles/send-invite/
    """
    if request.method == "POST":
        sender = get_request_user_profile(request.user)
        receiver = get_profile_by_pk(request)

        Relationship.objects.create(
            sender=sender,
            receiver=receiver,
            status="sent",
        )

    return redirect_back(request)


@login_required(login_url='/')
def remove_friend(request):
    """
    Deletes relationship between request's profile and target profile.
    View url: /profiles/remove-friend/
    """
    if request.method == "POST":
        sender = get_request_user_profile(request.user)
        receiver = get_profile_by_pk(request)

        # Find relationship
        # where sender is request's profile and receiver is target profile
        # or where sender is target profile and receiver is request's profile,
        # then delete it
        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver))
            | (Q(sender=receiver) & Q(receiver=sender)),
        )
        rel.delete()

    return redirect_back(request)


# Class-based views


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Shows target profile and it's details.
    View url: /profiles/users/<slug>/
    """

    model = Profile
    template_name = "profiles/profile_detail.html"
    form_class = CommentCreateModelForm

    def get(self, request, *args, **kwargs):

        # Redirect to profiles/myprofile/
        # if request's user == target user
        if Profile.objects.get(user=self.request.user) == self.get_object():
            return redirect("profiles:my-profile-view")

        # Default BaseDetailView.get parameters
        # (this has to be here)
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        # Add comment form
        form = self.form_class(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.profile = get_request_user_profile(self.request.user)
            instance.post = Post.objects.get(id=request.POST.get("post_id"))
            instance.save()

            form = CommentCreateModelForm()

            return redirect_back(self.request)

    def get_object(self):
        slug = self.kwargs.get("slug")
        profile = Profile.objects.get(slug=slug)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = get_request_user_profile(self.request.user)
        following = profile.following.all

        invited_users, incoming_invite_users = get_relationship_users(profile)

        context["invited_users"] = invited_users
        context["incoming_invite_users"] = incoming_invite_users
        context["following"] = following
        context["c_form"] = self.form_class
        context["avatar"] = profile.avatar.url
        context['name'] = profile.user
        context["profile"] = self.get_object()
        context["request_user_profile"] = profile

        context["posts"] = self.get_object().posts.all()

        return context


class ProfileListView(LoginRequiredMixin, ListView):
    """
    Shows list of all profiles except request's user.
    View url: /profiles/
    """

    model = Profile
    template_name = "profiles/profile_list.html"

    def get_queryset(self):
        qs = Profile.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = Profile.objects.get(user=self.request.user)
        following = profile.following.all

        invited_users, incoming_invite_users = get_relationship_users(profile)

        context["invited_users"] = invited_users
        context["incoming_invite_users"] = incoming_invite_users
        context["following"] = following
        context["profiles"] = self.get_queryset()

        return context


# class MessengerListView(VerificateRequiredMixin, ListView):
#     """
#     Shows list of all profiles except request's user.
#     View url: /profiles/messenger/
#     """
#     model = Profile
#     template_name = "profiles/messenger.html"

#     def get_queryset(self):
#         qs = get_friends_of_user(self.request.user)
#         return qs
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["profiles"] = self.get_queryset()

#         return context
def messanger_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.profile.is_verificated:
        return redirect('verificate')
    user = request.user
    profiles = []
    for profile in get_friends_of_user(request.user):
        profiles.append({'avatar': request.build_absolute_uri(f'/media/{profile.avatar}'), 'name': profile.user.username, 'url': f'/profiles/chat/{profile.slug}'})
    context = {
        'avatar': request.build_absolute_uri(f'/media/{user.profile.avatar}'),
        'name': user.username,
        'profiles': profiles
    }
    return render(request, 'profiles/messenger.html', context)

# class ChatMessageView(LoginRequiredMixin, ListView):
#     """
#     Shows messages between request's user and target user.
#     View url: /profiles/chat/<slug>/
#     """

#     model = Message
#     template_name = "profiles/chat.html"
#     form_class = MessageModelForm

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)

#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.sender = Profile.objects.get(user=self.request.user)
#             instance.receiver = self.get_object()
#             instance.save()

#         return redirect_back(self.request)

#     def get_object(self):
#         slug = self.kwargs.get("slug")
#         profile = Profile.objects.get(slug=slug)
#         return profile

#     def get_queryset(self):
#         profile = Profile.objects.get(user=self.request.user)

#         sent = Message.objects.filter(
#             sender=profile,
#             receiver=self.get_object(),
#         )
#         received = Message.objects.filter(
#             sender=self.get_object(),
#             receiver=profile,
#         )

#         messages = sent | received
#         ordered_messages = list(
#             messages.order_by("-created").values_list("content", flat=True),
#         )

#         return ordered_messages

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # Used to check which messages are received and which are sent
#         context["received"] = get_received_messages(
#             self.get_object(),
#             Profile.objects.get(user=self.request.user),
#         )
#         context["are_friends"] = check_if_friends(
#             self.get_object(),
#             self.request.user,
#         )
#         context["profile"] = self.get_object()
#         context["form"] = self.form_class
#         context["qs"] = self.get_queryset()

#         return context
def view_chat(request, slug):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.profile.is_verificated:
            return redirect('verificate')
        user = request.user
        try:
            friend = Profile.objects.get(slug=slug)
        except:
            return redirect_back(request)
        if not check_if_friends(friend, request.user):
            return redirect_back(request)
        profile = Profile.objects.get(user=user)
        sent = Message.objects.filter(
            sender=profile,
            receiver=friend,
        )
        received = Message.objects.filter(
            sender=friend,
            receiver=profile,
        )
        messages = sent | received
        ordered_messages = list(
            messages.order_by("-created").values("content", "created"),
        )
        context = {
            'avatar': request.build_absolute_uri(f'/media/{user.profile.avatar}'),
            'name': request.user.username,
            'friend_avatar': request.build_absolute_uri(f'/media/{friend.avatar}'),
            'friend_name': friend.user.username,
            'messages': ordered_messages,
            "received": [i.content for i in received],
            "sent": [i.content for i in sent]
        }
        return render(request, 'profiles/chat.html', context)
    else:
        content = request.POST.get('content')
        if not content.isspace():
            instance = Message.objects.create(sender=Profile.objects.get(user=request.user), receiver=Profile.objects.get(slug=slug), content=content)
        return redirect_back(request)