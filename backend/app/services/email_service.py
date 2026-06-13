import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger("ma_dd.email")

_SMTP_HOST: str = ""
_SMTP_PORT: int = 587
_SMTP_USER: str = ""
_SMTP_PASS: str = ""
_SMTP_FROM: str = ""
_SMTP_TLS: bool = True


def configure_smtp(host: str, port: int, user: str, password: str, from_addr: str, use_tls: bool = True):
    global _SMTP_HOST, _SMTP_PORT, _SMTP_USER, _SMTP_PASS, _SMTP_FROM, _SMTP_TLS
    _SMTP_HOST = host
    _SMTP_PORT = port
    _SMTP_USER = user
    _SMTP_PASS = password
    _SMTP_FROM = from_addr
    _SMTP_TLS = use_tls


def is_configured() -> bool:
    return bool(_SMTP_HOST and _SMTP_USER and _SMTP_PASS)


def _send_email(to: str, subject: str, html: str) -> bool:
    if not is_configured():
        logger.warning("SMTP not configured — email not sent to %s", to)
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = _SMTP_FROM or settings.firm_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=10) as server:
            if _SMTP_TLS:
                server.starttls()
            server.login(_SMTP_USER, _SMTP_PASS)
            server.send_message(msg)
        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False


def send_analysis_complete(deal_name: str, doc_count: int, issue_count: int, recipient_email: str):
    subject = f"[{settings.brand_name}] Analysis Complete — {deal_name}"
    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #4338ca, #312e81); padding: 24px; text-align: center; border-radius: 12px 12px 0 0;">
        <h1 style="color: #fff; margin: 0; font-size: 20px;">⚖️ {settings.brand_name}</h1>
    </div>
    <div style="padding: 24px; border: 1px solid #e2e8f0; border-top: 0; border-radius: 0 0 12px 12px;">
        <h2 style="margin-top: 0;">Document Analysis Complete</h2>
        <p>Due diligence analysis for <strong>{deal_name}</strong> has been completed.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 8px; border: 1px solid #e2e8f0; text-align: center;"><strong>{doc_count}</strong><br/>Documents</td>
                <td style="padding: 8px; border: 1px solid #e2e8f0; text-align: center;"><strong>{issue_count}</strong><br/>Issues Found</td></tr>
        </table>
        <p style="color: #666; font-size: 12px;">Log in to view detailed results and generate the DD report.</p>
        <p style="color: #666; font-size: 12px;">&mdash; {settings.firm_name}</p>
    </div></body></html>
    """
    return _send_email(recipient_email, subject, html)


def send_report_ready(deal_name: str, deal_id: str, recipient_email: str):
    subject = f"[{settings.brand_name}] DD Report Ready — {deal_name}"
    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #4338ca, #312e81); padding: 24px; text-align: center; border-radius: 12px 12px 0 0;">
        <h1 style="color: #fff; margin: 0; font-size: 20px;">⚖️ {settings.brand_name}</h1>
    </div>
    <div style="padding: 24px; border: 1px solid #e2e8f0; border-top: 0; border-radius: 0 0 12px 12px;">
        <h2 style="margin-top: 0;">Due Diligence Report Ready</h2>
        <p>The comprehensive DD report for <strong>{deal_name}</strong> has been generated.</p>
        <p>Download the report from the deal dashboard.</p>
        <p style="color: #666; font-size: 12px;">&mdash; {settings.firm_name}</p>
    </div></body></html>
    """
    return _send_email(recipient_email, subject, html)


def send_password_reset(user_name: str, user_email: str, token: str):
    reset_url = f"{settings.firm_base_url or 'http://localhost:3000'}/reset-password?token={token}"
    subject = f"[{settings.brand_name}] Password Reset Request"
    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #4338ca, #312e81); padding: 24px; text-align: center; border-radius: 12px 12px 0 0;">
        <h1 style="color: #fff; margin: 0; font-size: 20px;">⚖️ {settings.brand_name}</h1>
    </div>
    <div style="padding: 24px; border: 1px solid #e2e8f0; border-top: 0; border-radius: 0 0 12px 12px;">
        <h2 style="margin-top: 0;">Password Reset</h2>
        <p>Hi {user_name},</p>
        <p>A password reset was requested for your <strong>{settings.brand_name}</strong> account.</p>
        <p style="text-align: center; margin: 24px 0;">
            <a href="{reset_url}" style="background: linear-gradient(135deg, #4f46e5, #4338ca); color: #fff; padding: 12px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; display: inline-block;">Reset Password</a>
        </p>
        <p style="color: #888; font-size: 12px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
        <p style="color: #666; font-size: 12px;">&mdash; {settings.firm_name}</p>
    </div></body></html>
    """
    return _send_email(user_email, subject, html)


def send_welcome_email(user_name: str, user_email: str):
    subject = f"Welcome to {settings.brand_name}"
    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #4338ca, #312e81); padding: 24px; text-align: center; border-radius: 12px 12px 0 0;">
        <h1 style="color: #fff; margin: 0; font-size: 20px;">⚖️ {settings.brand_name}</h1>
    </div>
    <div style="padding: 24px; border: 1px solid #e2e8f0; border-top: 0; border-radius: 0 0 12px 12px;">
        <h2 style="margin-top: 0;">Welcome, {user_name}!</h2>
        <p>Your account for <strong>{settings.brand_name}</strong> has been created.</p>
        <p>You can now create deal rooms, upload documents, and run AI-powered due diligence analysis under Indian regulatory frameworks.</p>
        <p style="color: #666; font-size: 12px;">&mdash; {settings.firm_name}</p>
    </div></body></html>
    """
    return _send_email(user_email, subject, html)
