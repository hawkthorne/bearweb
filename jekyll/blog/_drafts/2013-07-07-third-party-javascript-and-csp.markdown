---
layout: post
title:  Content Security Policy and Google Analytics
date:   2013-07-07 10:00:00
author: Kyle Conroy
categories: engineering
---

[Content Security Policy][csp] is a new standard for securing your web
application against common attacks such as XSS. It works by limiting the
sources that content is allow to come from. For example, you can easily declare
that all content must only from your domain. The browser will then block any
other requests made.

The fine folks at GitHub wrote a [fantastic blog post][github] about setting up
your web application to use the Content Security Policy headers.

Many services, such as Google Analytics, Intercom, Twitter, distribute a
Javascript code snippet for you to include on your website. These snippets
offer various features, but current implementations break when using Content
Security Policy.

## Data Attributes

Many snippets use global Javascript objects to contain configuration
information. For example, here is the snippet for Intercom.

{% highlight ruby %}
<script id="IntercomSettingsScriptTag">
  window.intercomSettings = {
    email: "<%= current_user.email %>",
    created_at: <%= current_user.created_at.to_i %>,
    app_id: "f4be75c2c97ac89511fb6747e3e3f56515d59f31"
  };
</script>
{% end highlight %}

This method will break with CSP because inline scripts are disabled by default.
Instead of saving this data to the `window` object, you should instead use a
div with data attributes.

{% highlight html %}
<div id="intercom-settings"
  data-email="<%= current_user.email %>"
  data-created-at="<%= current_user.created_at.to_i %>"
  data-app-id="123417264adfc123c1cfc1f2cf21ca"></div>
{% end highlight %}

## White listing domains

Let's take google analytics for a 

## Eval is Evil

[csp]: http://www.w3.org/TR/CSP/
[github]: https://github.com/blog/1477-content-security-policy
