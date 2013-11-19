## Working Environment

You have several options in setting up your working environment.  We recommend
using virtualenv to separate the dependencies of your project from your system's
python environment.  If on Linux or Mac OS X, you can also use virtualenvwrapper to help manage multiple virtualenvs across different projects.

First, make sure you are using virtualenv (http://www.virtualenv.org). Once
that's installed, create your virtualenv::

    $ make install

## Secrets

Various secret information is kept in environment variables, outside of source
control. You'll need the following keys for your local application to work
correctly.

    GITHUB_ID
    GITHUB_SECRET
    MAILGUN_KEY
    SENTRY_DSN
    SECRET_KEY
    DJANGO_SETTINGS_MODULE
    STRIPE_SECRET_KEY


## Running locally

To run the index locally, you can use two commands. The first reloads the
website whenever you make changes. To just run the web interface (without the
Docker Index and Registry API):

    $ make debug

If you make chanes, you'll need to kill the process and start over it again. To
run the full website, use

    $ make serve

To reach the host machine from the guest VM, you'll set up a network tunnel via SSH

    $ vagrant ssh -- -R 8000:localhost:8000

## End to End Testing

There is a tiny script end2end which will build and upload an image. You'll
need to change the username to your username. To test locally:

    vagrant up
    vagrant ssh -- -R 8000:localhost:8000
    cd /vagrant/tests
    sudo ./test-local

 To test stackmachine.com

    vagrant up
    vagrant ssh
    cd /vagrant/tests
    sudo ./test-production
