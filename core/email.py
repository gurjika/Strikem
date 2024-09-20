# core/email.py
from djoser.email import ActivationEmail as BaseActivationEmail

class ActivationEmail(BaseActivationEmail):
    template_name = 'core/activation_email.html'  # Path to your custom email template



    def get_context_data(self):
        # Get the default context from Djoser
        context = super().get_context_data()
        print(context)
        # Ensure that the needed variables are present in the context
        context['protocol'] = self.request.scheme  # 'http' or 'https'
        print(context['protocol'])
        context['domain'] = self.request.get_host()  # Domain name
        print(context['domain'])

    

        return context