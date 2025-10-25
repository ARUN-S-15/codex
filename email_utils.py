# email_utils.py - Email utilities for CODEX platform
import os
import secrets
from datetime import datetime, timedelta
from flask import url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

# Email configuration
MAIL_ENABLED = os.getenv('MAIL_ENABLED', 'False').lower() == 'true'

def init_mail(app):
    """Initialize Flask-Mail with configuration"""
    if MAIL_ENABLED:
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'CODEX Platform <noreply@codex.com>')
        
        mail = Mail(app)
        print("✅ Email system enabled")
        return mail
    else:
        # Email disabled - platform works fine without it for public learning
        return None

def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)

def send_verification_email(mail, user_email, username, verification_token, request_host):
    """Send email verification link"""
    if not mail or not MAIL_ENABLED:
        print(f"⚠️  Email not sent (disabled). Verification link: /verify-email/{verification_token}")
        return False
    
    try:
        verification_link = f"http://{request_host}/verify-email/{verification_token}"
        
        msg = Message(
            subject="⚡ Verify Your CODEX Account",
            recipients=[user_email]
        )
        
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 2rem; }}
                .content {{ padding: 40px; }}
                .content h2 {{ color: #1a1a2e; margin-top: 0; }}
                .content p {{ color: #666; line-height: 1.6; font-size: 1rem; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #10a37f 0%, #0d8b6d 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .button:hover {{ background: linear-gradient(135deg, #0d8b6d 0%, #0a7359 100%); }}
                .footer {{ background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 0.85rem; }}
                .features {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .features ul {{ list-style: none; padding: 0; margin: 0; }}
                .features li {{ padding: 8px 0; color: #444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ Welcome to CODEX</h1>
                </div>
                <div class="content">
                    <h2>Hi {username}! 👋</h2>
                    <p>Thanks for signing up for CODEX - your AI-powered coding platform!</p>
                    <p>Please verify your email address to activate your account and start coding:</p>
                    
                    <center>
                        <a href="{verification_link}" class="button">✅ Verify Email Address</a>
                    </center>
                    
                    <div class="features">
                        <p><strong>What you'll get access to:</strong></p>
                        <ul>
                            <li>💻 Multi-language compiler (Python, C, C++, Java, JavaScript)</li>
                            <li>🎓 12 LeetCode-style practice problems</li>
                            <li>🤖 AI-powered code assistance (Gemini 2.0)</li>
                            <li>💾 Save and share your projects</li>
                            <li>⚡ Code optimization and debugging tools</li>
                        </ul>
                    </div>
                    
                    <p style="color: #999; font-size: 0.9rem; margin-top: 30px;">
                        If you didn't create this account, please ignore this email.
                    </p>
                    <p style="color: #999; font-size: 0.9rem;">
                        This link will expire in 24 hours.
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 CODEX Platform. All rights reserved.</p>
                    <p>Powered by Judge0 API & Google Gemini AI</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f"✅ Verification email sent to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def send_password_reset_email(mail, user_email, username, reset_token, request_host):
    """Send password reset link"""
    if not mail or not MAIL_ENABLED:
        print(f"⚠️  Email not sent (disabled). Reset link: /reset-password/{reset_token}")
        return False
    
    try:
        reset_link = f"http://{request_host}/reset-password/{reset_token}"
        
        msg = Message(
            subject="🔒 Reset Your CODEX Password",
            recipients=[user_email]
        )
        
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 2rem; }}
                .content {{ padding: 40px; }}
                .content h2 {{ color: #1a1a2e; margin-top: 0; }}
                .content p {{ color: #666; line-height: 1.6; font-size: 1rem; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #ff5459 0%, #d43f44 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .button:hover {{ background: linear-gradient(135deg, #d43f44 0%, #b82f33 100%); }}
                .footer {{ background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 0.85rem; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Password Reset</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>We received a request to reset your password for your CODEX account.</p>
                    <p>Click the button below to create a new password:</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">🔑 Reset Password</a>
                    </center>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul style="margin: 10px 0 0 20px;">
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this, please ignore this email</li>
                            <li>Your password won't change until you create a new one</li>
                        </ul>
                    </div>
                    
                    <p style="color: #999; font-size: 0.9rem; margin-top: 30px;">
                        For security reasons, this link can only be used once.
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 CODEX Platform. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f"✅ Password reset email sent to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def send_welcome_email(mail, user_email, username):
    """Send welcome email after successful verification"""
    if not mail or not MAIL_ENABLED:
        return False
    
    try:
        msg = Message(
            subject="🎉 Welcome to CODEX - Let's Get Started!",
            recipients=[user_email]
        )
        
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #10a37f 0%, #0d8b6d 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 2rem; }}
                .content {{ padding: 40px; }}
                .content h2 {{ color: #1a1a2e; margin-top: 0; }}
                .content p {{ color: #666; line-height: 1.6; font-size: 1rem; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #10a37f 0%, #0d8b6d 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .feature-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0; }}
                .footer {{ background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 0.85rem; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 You're All Set!</h1>
                </div>
                <div class="content">
                    <h2>Welcome aboard, {username}! 🚀</h2>
                    <p>Your email has been verified and your account is now active!</p>
                    
                    <div class="feature-box">
                        <h3 style="margin-top: 0; color: #1a1a2e;">🎯 Quick Start Guide:</h3>
                        <ol style="color: #666; line-height: 1.8;">
                            <li><strong>Compiler:</strong> Write and execute code in 5 languages</li>
                            <li><strong>Practice:</strong> Solve 12 coding challenges</li>
                            <li><strong>AI Assistant:</strong> Get code explanations and optimizations</li>
                            <li><strong>Projects:</strong> Save and share your work</li>
                        </ol>
                    </div>
                    
                    <center>
                        <a href="http://localhost:5000/main" class="button">🚀 Start Coding Now</a>
                    </center>
                    
                    <p style="margin-top: 30px;">Need help? Check out our <a href="http://localhost:5000/docs">documentation</a> or contact support.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 CODEX Platform. Happy Coding!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f"✅ Welcome email sent to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending welcome email: {e}")
        return False
