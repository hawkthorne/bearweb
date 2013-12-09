---
layout: post
title:  Web development performance inside and outside a VM
date:   2013-07-19 23:31:58
author: Brandon Liu
categories: engineering
---

##### Update!

Per knotty66's suggestion on [Hacker News][hn], I added measurements with NFS
on VirtualBox instead of Shared Folders, which speed it up significantly.

##### Update 2!
joevandyk points out that NFS Shared Folders can help on VMware Fusion too.
Added measurements, which shave off a second or two on app boot.
Joe also tipped us off to this forum thread detailing other's experiences: [Shared folders slow using VMWare provider as well as VirtualBox][thread]

## Overview

Web development on a VM presents plenty of benefits over developing on your
host machine: developer environments are easy to distribute, can closely match
production, and can be recreated at will. [Vagrant][vagrant] already handles
many headaches around using VMs seamlessly, such as networking and shared
filesystems. However, many potential users worry about the performance hit of
developing in a VM.

I decided to quantify the difference for typical tasks using my 'native' OS X
machine, Vagrant with the [VirtualBox][virtualbox] provider, and Vagrant with
the (paid) [Fusion provider][fusionprovider] atop the (paid) [VMware
Fusion][vmwarefusion].

-----
### Test Setup

I'm using my relatively dinky 2012 MacBook Air - it has a Core i5 chip, an SSD,
and 8GB of memory. I was aiming to measure the difference between machines in
typical web development tasks, so don't take these numbers as absolutes.

I chose to do my measurements on the [Discourse][discourse] forum application.
It's written in Ruby on Rails and has a fairly large test suite that's
comparable in size and complexity to most company's applications. Also, it's
free and open source, so please do try to reproduce these results yourself!

For both VirtualBox and Fusion, I allocated 2GB of RAM to the guest machine. I
tried these tests again using only 1GB, but it didn't make a significant
difference. The guests are running a typical set of services: redis, postgres,
nginx.

VirtualBox was also tested with NFS instead of Shared Folders, which has 
speed benefits outlined here: http://docs-v1.vagrantup.com/v1/docs/nfs.html
However, you might not be able to use it if your host machine doesn't support NFS.

-----
#### Application boot time

I measured the boot time of the application via the following script:

{% highlight bash %}
time `bundle exec script/rails runner "0"`
{% endhighlight %}
    
    
Application boot time is one serious source of friction for developers,
especially if you're doing test-driven development (which you should be!). Note
i'm using Ruby 2.0.0, which improves the performance of the `require` method
significantly over 1.9.3. 10 seconds is a heck of a long time to wait for the
app to start - if you're interested in improving this check out
[nailgun][nailgun] (JRuby), [spork][spork] and [zeus][zeus].

I ran the script three times on each machine and recorded the wall clock time:

##### Host Machine:

{% highlight bash %}
real	0m9.173s
real	0m8.739s
real	0m8.823s
{% endhighlight %}
    
##### VirtualBox w/ Shared folders:

{% highlight bash %}
real	0m21.764s
real	0m19.342s
real	0m20.674s
{% endhighlight %}

##### VirtualBox w/ NFS:

{% highlight bash %}
real	0m9.500s
real	0m8.669s
real	0m8.625s
{% endhighlight %}

##### VMware Fusion w/ Shared Folders:

{% highlight bash %}
real	0m10.587s
real	0m10.095s
real	0m10.445s
{% endhighlight %}

##### VMware Fusion w/ NFS:

{% highlight bash %}
real	0m8.315s
real	0m8.781s
real	0m8.445s
{% endhighlight %}

-----

#### Time for total test suite

I measured the time it took to run the entire Discourse test suite by simply calling:

{% highlight bash %}
bundle exec rake spec
{% endhighlight %}
    
The Discourse suite has 2672 individual test cases.

##### Host Machine:


{% highlight bash %}
Finished in 4 minutes 19.64 seconds
Finished in 3 minutes 52.26 seconds
Finished in 4 minutes 1.03 seconds
{% endhighlight %}

    
##### VirtualBox w/ Shared Folders:

{% highlight bash %}
Finished in 5 minutes 31.31 seconds
Finished in 5 minutes 12.14 seconds
Finished in 5 minutes 32.54 seconds
{% endhighlight %}

##### VirtualBox w/ NFS:

{% highlight bash %}
Finished in 4 minutes 42.27 seconds
Finished in 4 minutes 16.27 seconds
Finished in 4 minutes 43.79 seconds
{% endhighlight %}

##### VMware Fusion w/ Shared Folders:

{% highlight bash %}
Finished in 4 minutes 16.68 seconds
Finished in 4 minutes 23.95 seconds
Finished in 4 minutes 22.87 seconds
{% endhighlight %}

##### VMware Fusion w/ NFS:

{% highlight bash %}
Finished in 4 minutes 20.28 seconds
Finished in 4 minutes 15.43 seconds
Finished in 4 minutes 10.78 seconds
{% endhighlight %}

-----

### Therefore…

VMware Fusion and VirtualBox+NFS are considerably faster than 
VirtualBox+Shared Folders, and only slightly behind using the host machine. 

Using either VM solution in this case also has the nice advantage over
the host machine in that you can halt the VM when you're not developing to free
up all its resources! 

Please let us know at [hello@stackmachine.com][email] about your own
experiences with this!

### Addendum

I looked a little more into I/O performance for routines like accessing the database that would affect the speed of integration tests.
[pgbench][pgbench] ships with postgres and is a simple albeit synthetic way to measure postgresql performance.
In each case the postgres configuration is the default with `shared_buffers` set to 24MB and autovacuum off. The script I used:

{% highlight bash %}
createdb pgbench
pgbench -i -s 10 pgbench # use scalefactor = 10
pgbench -T 600 pgbench # collect results over 10 minutes
{% endhighlight %}

##### Host Machine:

{% highlight bash %}
transaction type: TPC-B (sort of)
scaling factor: 10
query mode: simple
number of clients: 1
number of threads: 1
duration: 600 s
number of transactions actually processed: 673985
tps = 1123.322847 (including connections establishing)
tps = 1123.328761 (excluding connections establishing)
{% endhighlight %}

##### VirtualBox:

{% highlight bash %}
number of transactions actually processed: 421642
tps = 702.709747 (including connections establishing)
tps = 702.713031 (excluding connections establishing)
{% endhighlight %}

##### VMware Fusion:

{% highlight bash %}
number of transactions actually processed: 558332
tps = 930.552663 (including connections establishing)
tps = 930.557223 (excluding connections establishing)
{% endhighlight %}

So in raw database performance, VMWare is about 20% slower than the host machine, and VirtualBox is 20% slower still - these differences didn't correlate to the real-world cases above, though.

[vagrant]: http://www.vagrantup.com
[virtualbox]: http://www.virtualbox.com
[vmwarefusion]: http://www.vmware.com/products/fusion/overview.html
[fusionprovider]: http://www.vagrantup.com/vmware
[spork]: https://github.com/sporkrb/spork
[nailgun]: https://github.com/martylamb/nailgun
[zeus]: https://github.com/burke/zeus
[discourse]: https://github.com/discourse/discourse
[email]: mailto:hello@stackmachine.com
[antifuchs]: https://twitter.com/antifuchs
[pgbench]: http://www.postgresql.org/docs/devel/static/pgbench.html 
[hn]: https://news.ycombinator.com/item?id=6085695
[thread]: http://vagrant.1086180.n5.nabble.com/Shared-folders-slow-using-VMWare-provider-as-well-as-VirtualBox-td935.html
