document.addEventListener("DOMContentLoaded", function () {
  // Initialize Stripe with your publishable key
  var stripe = Stripe('pk_test_51OfOHSSCpDiVJdt3aAyYglxpc8TGzue5X2KT88cFFx77WwxjDkgDg9ohWy9AJKJEg5ifnOyFPG02BGkJshkfG75q004MZ5bmGX');

  // Create a Payment Element
  var elements = stripe.elements();
  var paymentElement = elements.create('payment', {
      // Customize fields as needed
      fields: {
          billingDetails: {
              name: 'auto',
              phone: 'auto',
              address: 'never',
              card: 'never'
          }
      }
  });

  // Mount the Payment Element to the DOM
  paymentElement.mount('#payment-element');

  // Handle form submission
  var form = document.getElementById('payment-form');
  form.addEventListener('submit', function (event) {
      event.preventDefault();

      // Confirm payment using Stripe.js
      stripe.confirmPayment({
          elements: elements,
          confirmParams: {
              return_url: 'your_return_url_here', // Replace with your actual return URL
              payment_method_data: {
                  billing_details: {
                      name: 'Jenny Rosen',
                      phone: '+91 XXXXXXXXXX'
                  }
              },
          },
      }).then(function (result) {
          if (result.error) {
              // Display error message to the user
              var errorElement = document.getElementById('payment-errors');
              errorElement.textContent = result.error.message;
          } else {
              // Redirect to home page or perform any other action
              window.location.href = '/'; // Redirect to the home page
          }
      });
  });
});
