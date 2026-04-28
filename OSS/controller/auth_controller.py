import random
import string

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from OSS.models import User, PasswordResetOTP, RegistrationOTP
from OSS.models.EmailChangeOTP import EmailChangeOTP
from OSS.models.forms import UserUpdateForm
from OSS.models.register import CustomUserRegistrationForm
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


# --- Rút gọn và hợp nhất REGISTER ---
def register_view(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            # commit=False để lấy object user ra nhưng chưa save vào DB vội
            user = form.save(commit=False)
            user.is_active = False # Chặn đăng nhập ngay từ đầu
            user.save() # Giờ mới save thật

            # Tạo mã OTP 6 số
            otp = ''.join(random.choices(string.digits, k=6))
            RegistrationOTP.objects.create(user=user, otp_code=otp)

            # Gửi mail (Mailtrap)
            send_mail(
                'Xác thực tài khoản Greenshop',
                f'Chào mừng {user.username}! Mã xác thực của bạn là: {otp}',
                'no-reply@greenshop.com',
                [user.email],
                fail_silently=False,
            )

            # Lưu ID vào session để trang xác thực biết là ai
            request.session['register_user_id'] = user.id
            messages.info(request, "Vui lòng kiểm tra email để lấy mã xác thực.")
            return redirect('verify_registration')
        else:
            messages.error(request, "Thông tin đăng ký không hợp lệ.")
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # AuthenticationForm mặc định không cho login nếu is_active=False
            # Nhưng để chắc chắn và báo lỗi rõ ràng hơn:
            if user.is_active:
                login(request, user)
                return redirect('admin_dashboard' if user.is_staff else 'home')
            else:
                messages.error(request, "Tài khoản của bạn chưa được xác thực. Vui lòng kiểm tra email.")
        else:
            # Kiểm tra xem có phải do tài khoản chưa active không
            username = request.POST.get('username')
            check_user = User.objects.filter(username=username).first()
            if check_user and not check_user.is_active:
                messages.warning(request, "Tài khoản chưa xác thực! Vui lòng nhập mã OTP đã gửi.")
                request.session['register_user_id'] = check_user.id
                return redirect('verify_registration')

            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Xử lý đăng xuất"""
    logout(request)
    messages.info(request, "Bạn đã đăng xuất thành công.")
    return redirect('home')


def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        new_email = request.POST.get('email')

        # 1. Kiểm tra nếu có sự thay đổi Email
        if new_email and new_email != request.user.email:
            # Check xem email mới có ai dùng chưa
            if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                messages.error(request, "Email này đã được người khác sử dụng!")
                return render(request, 'auth/profile.html', {'form': form})

            # 2. Tạo mã OTP gửi về Email MỚI
            otp = ''.join(random.choices(string.digits, k=6))
            EmailChangeOTP.objects.create(user=request.user, new_email=new_email, otp_code=otp)

            send_mail(
                'Xác nhận thay đổi Email - Greenshop',
                f'Mã xác nhận để đổi email của ông là: {otp}',
                'security@greenshop.com',
                [new_email],
            )

            # Lưu email mới vào session để dùng ở trang xác thực
            request.session['pending_new_email'] = new_email
            messages.info(request, f"Một mã xác thực đã được gửi tới {new_email}. Vui lòng kiểm tra!")
            return redirect('verify_email_change')

        # 3. Nếu không đổi email hoặc chỉ đổi Tên/Địa chỉ thì lưu luôn
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công!")
            return redirect('profile')

    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'auth/profile.html', {'form': form})

# Bước 1: Nhập Email và gửi mã
def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            # Tạo mã 6 số ngẫu nhiên
            otp = ''.join(random.choices(string.digits, k=6))
            PasswordResetOTP.objects.create(user=user, otp_code=otp)

            # Gửi mail qua Mailtrap
            send_mail(
                'Mã xác nhận đổi mật khẩu - Greenshop',
                f'Chào ông Tây, mã OTP của ông là: {otp}. Mã có hiệu lực trong 5 phút.',
                'admin@greenshop.com',
                [email],
                fail_silently=False,
            )
            request.session['reset_email'] = email # Lưu email vào session để dùng bước sau
            messages.success(request, "Mã OTP đã được gửi vào Email của ông.")
            return redirect('verify_otp')
        else:
            messages.error(request, "Email này không tồn tại trong hệ thống!")
    return render(request, 'auth/request_reset.html')

# Bước 2: Nhập và kiểm tra OTP
def verify_otp(request):
    email = request.session.get('reset_email')
    if not email: return redirect('request_reset')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        otp_record = PasswordResetOTP.objects.filter(
            user__email=email, otp_code=otp_input
        ).last()

        if otp_record and otp_record.is_valid():
            otp_record.is_used = True
            otp_record.save()
            request.session['otp_verified'] = True # Đánh dấu đã xác thực xong
            return redirect('reset_password_new')
        else:
            messages.error(request, "Mã OTP không đúng hoặc đã hết hạn!")
    return render(request, 'auth/verify_otp.html')

# Bước 3: Đặt mật khẩu mới
def reset_password_new(request):
    if not request.session.get('otp_verified'): return redirect('request_reset')

    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            email = request.session.get('reset_email')
            user = User.objects.get(email=email)
            user.set_password(new_password) # Django tự động hash pass ở đây
            user.save()

            # Xóa session sau khi xong việc
            del request.session['reset_email']
            del request.session['otp_verified']

            messages.success(request, "Đổi mật khẩu thành công! Mời ông đăng nhập lại.")
            return redirect('login')
        else:
            messages.error(request, "Mật khẩu xác nhận không khớp!")

    return render(request, 'auth/reset_password_new.html')


def verify_registration(request):
    user_id = request.session.get('register_user_id')
    if not user_id: return redirect('register')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        user = get_object_or_404(User, id=user_id)
        otp_record = RegistrationOTP.objects.filter(user=user, otp_code=otp_input).last()

        if otp_record and otp_record.is_valid():
            user.is_active = True # KÍCH HOẠT TÀI KHOẢN
            user.save()

            login(request, user) # Đăng nhập luôn cho tiện
            del request.session['register_user_id']
            messages.success(request, "Tài khoản đã được xác thực thành công!")
            return redirect('home')
        else:
            messages.error(request, "Mã xác thực không đúng hoặc đã hết hạn.")

    return render(request, 'auth/verify_registration.html')

def verify_email_change(request):
    new_email = request.session.get('pending_new_email')
    if not new_email:
        return redirect('profile')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        # Lấy bản ghi OTP mới nhất của user này cho email mới này
        otp_record = EmailChangeOTP.objects.filter(
            user=request.user,
            new_email=new_email,
            otp_code=otp_input
        ).last()

        if otp_record and otp_record.is_valid():
            # XÁC THỰC XONG -> CẬP NHẬT THẬT
            user = request.user
            user.email = new_email
            user.save()

            del request.session['pending_new_email']
            messages.success(request, f"Email đã được đổi thành {new_email} thành công!")
            return redirect('profile')
        else:
            messages.error(request, "Mã xác thực không đúng hoặc đã hết hạn.")

    return render(request, 'auth/verify_email_change.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        # PasswordChangeForm yêu cầu tham số đầu tiên là user
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Cập nhật lại session để User không bị logout
            update_session_auth_hash(request, user)
            messages.success(request, "Đổi mật khẩu thành công rồi nhé ông giáo!")
            return redirect('profile')
        else:
            messages.error(request, "Vui lòng sửa lỗi bên dưới.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'auth/change_password.html', {'form': form})