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
        # Get the context data from the original method
        context = self.get_context_data()

        # Generate the activation link using the protocol and domain
        protocol = 'http'
        domain = context.get('domain')  # You might want to get this from your settings or generate it
        uid = context.get('uid')
        token = context.get('token')
      

        # Add the user email to the context
        context['domain'] = domain  # Pass the activation link to the template
        context['url'] = f'activate/{uid}/{token}/'
        context['protocol'] = protocol

        # Render the email template with the context

        subject = "Activate your PoolHub Account"
        html_content = render_to_string('email/activation.html', context)

        # Create email message
        email_message = EmailMultiAlternatives(
            subject, '', settings.DEFAULT_FROM_EMAIL, to
        )


        email_message.attach_alternative(html_content, 'text/html')

        # Send the email
        email_message.send(fail_silently=False)



        # send_mail(
        #     subject='Poolhub Reservation',
        #     message='activate account',
        #     from_email='luka.gurjidze04@gmail.com',
        #     recipient_list=to,
        #     fail_silently=False ## TESTING
        # )