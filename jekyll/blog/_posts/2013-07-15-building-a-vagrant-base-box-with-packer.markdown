---
layout: post
title:  Building a Vagrant base box with Packer
date:   2013-07-15 23:31:58
author: Brandon Liu
hidden: true
categories: engineering
---

[Packer][packer] is a utility to create disk images for platforms like VirtualBox, VMWare Fusion, Amazon EC2 and DigitalOcean. It can be used to build [Vagrant][vagrant] base boxes, which can be shared within your team to make portable development environments.

One way to build a Vagrant base box with packer is to convert a veewee template using [veewee-to-packer][v2p], however I wanted to build a more minimal box that doesn't have Ruby, Chef or Puppet. These are usually suggested for provisioning on top of your base box (see the [Vagrant base box documentation][baseboxdocs]), instead I'm going to use the [prefab][prefab] configuration manager, which is a standalone binary.

Here's a minimal template to build an Ubuntu base box: [ubuntu64.json][ubuntu64]. There's a couple of quirky bits to point out:

### preseed.cfg

{% highlight javascript %}
  "http_directory": "preseed" 
{% endhighlight %}

A directory of files to serve. When installing from the operating system ISO, you can give it a `preseed.cfg` answers file
which will automate configuring the box for the first time. It sets settings such as the login user and password, keyboard settings,
and the disk layout. Here's the preseed.cfg for a vagrant base box: [preseed.cfg][preseed]

### Password-less login and sudo for the 'vagrant' user

{% highlight javascript %}
      "mkdir ~/.ssh",
      "wget -qO- https://raw.github.com/mitchellh/vagrant/master/keys/vagrant.pub >> ~/.ssh/authorized_keys",
{% endhighlight %}

Lets the `vagrant` user ssh without a password, as long as you're using the vagrant client which includes its own private key.

{% highlight javascript %}
"(cat <<'vagrant ALL=NOPASSWD:ALL') > /tmp/vagrant",
"chmod 0440 /tmp/vagrant",
"mv /tmp/vagrant /etc/sudoers.d/"
{% endhighlight %}

Let the `vagrant` user use `sudo` without prompting for a password.

### VirtualBox guest additions

When installing the VirtualBox guest additions you may run into an error message that looks like this:

{% highlight bash %}
    virtualbox: Installing the Window System drivers ...fail!
    virtualbox: (Could not find the X.Org or XFree86 Window System.)
{% endhighlight %}

You can ignore the error, unless you want to install the X Window System on your VM. You probably don't need it, and it's quite large.

### Shutdown Command

{% highlight javascript %}
"shutdown_command": "echo 'shutdown -P now' > shutdown.sh; echo 'vagrant'|sudo -S sh 'shutdown.sh'"
{% endhighlight %}

The `shutdown_command` is necessary, otherwise Packer will simply poweroff the machine, and any changes you've made in your provisioner
that have not yet been persisted to disk might be lost.

If you'd like to use the resulting box here's a link to it: [ubuntu64.box][ubuntu64box]

[packer]:    http://packer.io
[ubuntu64]: https://github.com/stackmachine/packer-templates/blob/master/ubuntu64.json
[preseed]: https://github.com/stackmachine/packer-templates/blob/master/preseed/preseed.cfg
[v2p]: https://github.com/mitchellh/veewee-to-packer
[baseboxdocs]: http://docs-v1.vagrantup.com/v1/docs/base_boxes.html
[prefab]: http://stackmachine.github.io/prefab/
[vagrant]: http://www.vagrantup.com
[ubuntu64box]: https://s3.amazonaws.com/dl.stackmachine.com/baseboxes/ubuntu64.box
