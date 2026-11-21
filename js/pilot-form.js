/* First-party helper for the Pricing and pilot form.
   Validates the fields and opens a pre-filled mailto. Nothing is sent to this site. */
(function () {
  "use strict";

  var form = document.getElementById("pilot-form");
  if (!form) {
    return;
  }

  var CONTACT = form.getAttribute("data-contact") || "Empoweru25@outlook.com";
  var summary = document.getElementById("pilot-form-errors");
  var SIZE_VALUES = {
    "1-10": "1-10 people",
    "11-50": "11-50 people",
    "51-200": "51-200 people",
    "201-1000": "201-1,000 people",
    "1000+": "1,000+ people"
  };
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  var fields = {
    name: {
      input: document.getElementById("pilot-name"),
      error: document.getElementById("pilot-name-error"),
      check: function (value) {
        if (value.length < 2) {
          return "Enter your name (at least 2 characters).";
        }
        if (value.length > 80) {
          return "Name must be 80 characters or fewer.";
        }
        return "";
      }
    },
    company: {
      input: document.getElementById("pilot-company"),
      error: document.getElementById("pilot-company-error"),
      check: function (value) {
        if (value.length < 2) {
          return "Enter your company name (at least 2 characters).";
        }
        if (value.length > 80) {
          return "Company must be 80 characters or fewer.";
        }
        return "";
      }
    },
    email: {
      input: document.getElementById("pilot-email"),
      error: document.getElementById("pilot-email-error"),
      check: function (value) {
        if (!value) {
          return "Enter a work email address.";
        }
        if (value.length > 254 || !EMAIL_RE.test(value)) {
          return "Enter a valid email address.";
        }
        return "";
      }
    },
    size: {
      input: document.getElementById("pilot-size"),
      error: document.getElementById("pilot-size-error"),
      check: function (value) {
        if (!Object.prototype.hasOwnProperty.call(SIZE_VALUES, value)) {
          return "Select a company size.";
        }
        return "";
      }
    },
    message: {
      input: document.getElementById("pilot-message"),
      error: document.getElementById("pilot-message-error"),
      check: function (value) {
        if (value.length < 10) {
          return "Enter a short message (at least 10 characters).";
        }
        if (value.length > 2000) {
          return "Message must be 2,000 characters or fewer.";
        }
        return "";
      }
    }
  };

  function valueOf(field) {
    return (field.input.value || "").trim();
  }

  function setError(field, message) {
    if (!field.input || !field.error) {
      return;
    }
    if (message) {
      field.input.setAttribute("aria-invalid", "true");
      field.error.textContent = message;
      field.error.hidden = false;
    } else {
      field.input.removeAttribute("aria-invalid");
      field.error.textContent = "";
      field.error.hidden = true;
    }
  }

  function validate() {
    var errors = [];
    var firstInvalid = null;
    Object.keys(fields).forEach(function (key) {
      var field = fields[key];
      var message = field.check(valueOf(field));
      setError(field, message);
      if (message) {
        errors.push(message);
        if (!firstInvalid) {
          firstInvalid = field.input;
        }
      }
    });
    return { errors: errors, firstInvalid: firstInvalid };
  }

  function showSummary(errors) {
    if (!summary) {
      return;
    }
    if (!errors.length) {
      summary.hidden = true;
      summary.textContent = "";
      return;
    }
    summary.hidden = false;
    summary.textContent =
      errors.length === 1
        ? "Please fix this item: " + errors[0]
        : "Please fix " + errors.length + " items in the form before opening the email.";
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var result = validate();
    showSummary(result.errors);
    if (result.errors.length) {
      if (result.firstInvalid) {
        result.firstInvalid.focus();
      }
      return;
    }

    var name = valueOf(fields.name);
    var company = valueOf(fields.company);
    var email = valueOf(fields.email);
    var size = valueOf(fields.size);
    var message = valueOf(fields.message);
    var subject = "Pilot inquiry from " + name + " at " + company;
    var body = [
      "Name: " + name,
      "Company: " + company,
      "Email: " + email,
      "Company size: " + SIZE_VALUES[size],
      "",
      "Message:",
      message
    ].join("\r\n");
    var url =
      "mailto:" +
      CONTACT +
      "?subject=" +
      encodeURIComponent(subject) +
      "&body=" +
      encodeURIComponent(body);
    window.location.href = url;
  });
})();
