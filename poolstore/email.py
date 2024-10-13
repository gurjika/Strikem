from django.conf import settings
from djoser.email import ActivationEmail
from django.core.mail import EmailMultiAlternatives, send_mail


from djoser.email import ActivationEmail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class CustomActivationEmail(ActivationEmail):
    template_name = 'email/activation.html'
    def send(self, to):
        context = self.get_context_data()

        
        protocol = 'http'
        domain = context.get('domain') 
        uid = context.get('uid')
        token = context.get('token')
      

        context['domain'] = domain  
        context['url'] = f'users/activate/{uid}/{token}/'
        context['protocol'] = protocol


        subject = "Activate your PoolHub Account"
        html_content = render_to_string('email/activation.html', context)

        email_message = EmailMultiAlternatives(
            subject, '', settings.DEFAULT_FROM_EMAIL, to
        )


        email_message.attach_alternative(html_content, 'text/html')

        email_message.send(fail_silently=False)

