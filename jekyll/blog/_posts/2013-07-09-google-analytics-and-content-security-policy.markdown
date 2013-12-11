---
layout: post
title:  Google Analytics and Content Security Policy
date:   2013-07-09 10:00:00
author: Kyle Conroy
categories: engineering
---

[Content Security Policy (CSP)][csp] is a new header for securing your web
application against common scripting attacks. It works by limiting content
sources a web page is allowed to access. For example, the header can declare
that all content (images, scripts, frames) must originate from a single domain.
The browser will block any requests that violate this policy.

CSP defaults to also blocking inline styles, inline Javascript, and the use of
`eval` in Javascript. These defaults have a high risk of breaking existing
sites. Specifically, the Javascript code snippet that Google Analytics asks you
to include on your website implementations break when using Content Security
Policy.

## Content Security Policy Header

CSP is implemented by returning the `Content-Security-Policty` header to web
requests. The header specifies the allowed domains for content sources. The
`default-src` applies to all unspecified content. The `'self'` value represents
the domain which served this response.

The header below allows all content from the current domain, and allows scripts
from one additional domain, `https://ssl.google-analytics.com`.

{% highlight text %}
Content-Security-Policy: "default-src 'self'; script-src 'self' https://ssl.google-analytics.com"
{% endhighlight %}

With this header in place, let's see what happens when we load our page with a
Google Analytics tracking snippet.

<img style="max-width:514px" src="/static/img/csp-violation.png" alt="CSP Violation" />

Uh-oh.

## Javascript Changes

Google Analytics suggests you add the following snippet to all you pages.

{% highlight html %}
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-22222222-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
{% endhighlight %}

This snippet will violate the above content policy as it includes inline
Javascript. We could change our content policy to allow inline Javascript, but
that would defeat the entire purpose of adding the header.  Instead, we'll
break apart the above snippet into two script tags. First, create a new
Javascript file named `tracking.js` with the following content:

{% highlight javascript %}
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-22222222-1']);
_gaq.push(['_trackPageview']);
{% endhighlight %}

Remove the Google Analytics tracking snippet and replace it with these two scripts.

{% highlight html %}
<script type="text/javascript" src="/js/tracking.js"></script>
<script src="https://ssl.google-analytics.com/ga.js" async="true"></script>
{% endhighlight %}

Make sure that these scripts appear at the bottom of the page right before the
closing body tag. Older browsers don't honor the `async` attribute, so you want
to make sure it's the last script to load.

Refresh the page, and you should see that Google Analytics is working as intended.

<img style="max-width:571px"  src="/static/img/csp-ok.png" alt="CSP Ok" />

Please remember that CSP is just another tool to help secure your web
application and does not replace proper HTML escaping. Browsers without CSP
support need to be protected as well.

For a deeper look into CSP, the fine folks at GitHub wrote a [fantastic
post][github] about their experience implementing CSP.


[csp]: http://www.w3.org/TR/CSP/
[github]: https://github.com/blog/1477-content-security-policy
