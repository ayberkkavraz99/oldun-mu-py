"""
E-posta servisi
"""
from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import get_settings

settings = get_settings()


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    E-posta gönder
    
    Args:
        to_email: Alıcı e-posta adresi
        subject: Konu
        html_content: HTML içerik
        text_content: Düz metin içerik (opsiyonel)
    
    Returns:
        Başarılı ise True
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[EMAIL] SMTP yapılandırılmamış. E-posta gönderilemiyor: {to_email}")
        return False
    
    try:
        message = MIMEMultipart("alternative")
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        if text_content:
            message.attach(MIMEText(text_content, "plain", "utf-8"))
        
        message.attach(MIMEText(html_content, "html", "utf-8"))
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        
        print(f"[EMAIL] E-posta gönderildi: {to_email}")
        return True
    
    except Exception as e:
        print(f"[EMAIL] E-posta gönderme hatası: {e}")
        return False


async def send_verification_email(email: str, ad: str, kod: str) -> bool:
    """E-posta doğrulama kodu gönder"""
    subject = "Öldün mü? - E-posta Doğrulama"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .code {{ font-size: 32px; font-weight: bold; color: #4F46E5; text-align: center; 
                     padding: 20px; background: white; border-radius: 8px; margin: 20px 0; letter-spacing: 8px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Öldün mü?</h1>
            </div>
            <div class="content">
                <p>Merhaba <strong>{ad}</strong>,</p>
                <p>Hesabınızı oluşturduğunuz için teşekkür ederiz. E-posta adresinizi doğrulamak için aşağıdaki kodu kullanın:</p>
                <div class="code">{kod}</div>
                <p>Bu kod 24 saat geçerlidir.</p>
                <p>Eğer bu hesabı siz oluşturmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Öldün mü? - Güvenliğiniz için buradayız.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(email, subject, html_content)


async def send_password_reset_email(email: str, ad: str, token: str) -> bool:
    """Şifre sıfırlama e-postası gönder"""
    subject = "Öldün mü? - Şifre Sıfırlama"
    reset_link = f"{settings.FRONTEND_URL}/sifre-sifirla?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #DC2626; color: white; padding: 12px 30px; 
                       text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Şifre Sıfırlama</h1>
            </div>
            <div class="content">
                <p>Merhaba <strong>{ad}</strong>,</p>
                <p>Şifrenizi sıfırlamak için bir istek aldık. Şifrenizi sıfırlamak için aşağıdaki butona tıklayın:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Şifremi Sıfırla</a>
                </p>
                <p>Bu link 1 saat geçerlidir.</p>
                <p>Eğer bu isteği siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Öldün mü? - Güvenliğiniz için buradayız.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(email, subject, html_content)


async def send_alarm_notification_email(email: str, ad: str, kullanici_adi: str, mesaj: str) -> bool:
    """Acil durum alarm bildirimi gönder"""
    subject = "🚨 ACİL DURUM - Öldün mü? Alarm Bildirimi"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #FEE2E2; padding: 30px; border-radius: 0 0 8px 8px; border: 2px solid #DC2626; }}
            .alert {{ font-size: 18px; font-weight: bold; color: #DC2626; text-align: center; margin-bottom: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 ACİL DURUM ALARMI</h1>
            </div>
            <div class="content">
                <p class="alert">Bu bir acil durum bildirimidir!</p>
                <p>Merhaba <strong>{ad}</strong>,</p>
                <p><strong>{kullanici_adi}</strong> sizi acil durum kişisi olarak eklemiştir ve bir alarm tetiklendi.</p>
                {f'<p><strong>Mesaj:</strong> {mesaj}</p>' if mesaj else ''}
                <p style="font-weight: bold; color: #DC2626;">Lütfen en kısa sürede iletişime geçmeye çalışın.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Öldün mü? - Güvenliğiniz için buradayız.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(email, subject, html_content)
