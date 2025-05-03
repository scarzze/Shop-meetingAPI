from datetime import datetime
from app.models import Profile, PriceAlert, db
import requests
from config import Config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.utils.validators import PriceAlertSchema, NotificationSettingsSchema
import logging
import os
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.alert_schema = PriceAlertSchema()
        self.settings_schema = NotificationSettingsSchema()
        
    @staticmethod
    def check_price_alerts():
        """Check all active price alerts and notify users if conditions are met"""
        alerts = PriceAlert.query.filter_by(is_active=True).all()
        notification_results = []
        
        for alert in alerts:
            try:
                result = NotificationService._process_price_alert(alert)
                if result:
                    notification_results.append(result)
            except Exception as e:
                logger.error(f"Error processing alert {alert.id}: {str(e)}")
                continue
                
        return notification_results

    @staticmethod
    def _process_price_alert(alert: PriceAlert) -> Optional[Dict[str, Any]]:
        """Process individual price alert"""
        try:
            response = requests.get(
                f"{Config.PRODUCT_SERVICE_URL}/products/{alert.product_id}",
                timeout=5
            )
            response.raise_for_status()
            product = response.json()
            current_price = product.get('price')
            
            if not current_price:
                return None
                
            profile = Profile.query.get(alert.profile_id)
            if not profile:
                return None
                
            # Check if price drop meets threshold
            price_drop_percent = (alert.target_price - current_price) / alert.target_price
            min_threshold = profile.notification_settings.get('alert_threshold', 0.05)
            
            if current_price <= alert.target_price and price_drop_percent >= min_threshold:
                NotificationService.send_price_alert(
                    profile,
                    product,
                    current_price,
                    alert.target_price
                )
                alert.last_notified = datetime.utcnow()
                db.session.commit()
                
                return {
                    'alert_id': alert.id,
                    'profile_id': profile.id,
                    'product_id': product['id'],
                    'price_drop': price_drop_percent,
                    'status': 'notified'
                }
                
        except requests.RequestException as e:
            logger.error(f"API request failed for alert {alert.id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error in price alert processing: {str(e)}")
            
        return None

    @staticmethod
    def send_price_alert(profile: Profile, product: Dict[str, Any], current_price: float, target_price: float) -> bool:
        """Send price alert notification to user"""
        try:
            subject = f"Price Drop Alert: {product['name']}"
            price_drop_percent = ((target_price - current_price) / target_price) * 100
            
            body = f"""
            Great news! We found a price drop for an item on your alert list.
            
            Product: {product['name']}
            Current Price: ${current_price:.2f}
            Your Target: ${target_price:.2f}
            Price Drop: {price_drop_percent:.1f}%
            
            View the product now: {Config.FRONTEND_URL}/products/{product['id']}
            
            To manage your price alerts, visit:
            {Config.FRONTEND_URL}/profile/alerts
            
            If you wish to unsubscribe from price alerts, you can update your notification settings at:
            {Config.FRONTEND_URL}/profile/settings
            """
            
            return NotificationService.send_email(profile, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send price alert: {str(e)}")
            return False

    @staticmethod
    def send_device_login_alert(profile: Profile, device_session: Any) -> bool:
        """Send notification about new device login"""
        try:
            subject = "New Device Login Detected"
            body = f"""
            We detected a login from a new device:
            
            Device: {device_session.device_type}
            Time: {device_session.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            Location: {device_session.location or 'Unknown'}
            IP Address: {device_session.ip_address}
            
            If this wasn't you, please:
            1. Remove this device immediately: {Config.FRONTEND_URL}/profile/devices
            2. Change your password: {Config.FRONTEND_URL}/profile/security
            3. Contact support if needed: {Config.FRONTEND_URL}/support
            
            Stay safe!
            """
            
            return NotificationService.send_email(profile, subject, body, priority='high')
            
        except Exception as e:
            logger.error(f"Failed to send device login alert: {str(e)}")
            return False

    @staticmethod
    def send_email(profile: Profile, subject: str, body: str, priority: str = 'normal') -> bool:
        """Send email to user with error handling and logging"""
        if not profile or not hasattr(profile, 'email'):
            logger.error("Invalid profile or missing email")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_FROM
            msg['To'] = profile.email
            msg['Subject'] = subject
            
            if priority == 'high':
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {profile.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {profile.email}: {str(e)}")
            return False

    @staticmethod
    def send_preference_based_recommendations(profile: Profile) -> bool:
        """Send personalized product recommendations based on user preferences"""
        if not profile.preferences:
            return False
            
        favorite_categories = profile.preferences.get('favorite_categories', [])
        price_range = profile.preferences.get('preferred_price_range', {})
        
        if not favorite_categories and not price_range:
            return False
            
        try:
            params = {
                'limit': 5,
                'categories': ','.join(favorite_categories) if favorite_categories else None,
                'min_price': price_range.get('min'),
                'max_price': price_range.get('max')
            }
            
            response = requests.get(
                f"{Config.PRODUCT_SERVICE_URL}/products/recommendations",
                params={k: v for k, v in params.items() if v is not None},
                timeout=5
            )
            response.raise_for_status()
            products = response.json()
            
            if products:
                subject = "Products You Might Like"
                body = "Based on your preferences, we thought you might like these products:\n\n"
                
                for product in products:
                    body += f"- {product['name']}\n"
                    body += f"  Price: ${product['price']:.2f}\n"
                    body += f"  {Config.FRONTEND_URL}/products/{product['id']}\n\n"
                
                body += "\nManage your preferences and recommendations at:\n"
                body += f"{Config.FRONTEND_URL}/profile/preferences"
                
                return NotificationService.send_email(profile, subject, body)
                
            return False
            
        except requests.RequestException as e:
            logger.error(f"Failed to get recommendations: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error in recommendations process: {str(e)}")
            return False