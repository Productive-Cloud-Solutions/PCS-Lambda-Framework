# https://aws.amazon.com/blogs/compute/using-container-image-support-for-aws-lambda-with-aws-sam/
# https://gallery.ecr.aws/lambda/python

FROM public.ecr.aws/lambda/python:3.9.2022.12.14.07

RUN echo -e "[Stripe]\nname=stripe\nbaseurl=https://packages.stripe.dev/stripe-cli-rpm-local/\nenabled=1\ngpgcheck=0" >> /etc/yum.repos.d/stripe.repo

RUN yum install stripe -y

# https://stripe.com/docs/cli/login 

ENV XDG_CONFIG_HOME '/opt/python/settings/'

CMD [ "app.lambda_handler" ]