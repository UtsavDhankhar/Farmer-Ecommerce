<script>
        function getCsrf() {
            var inputElems = document.querySelectorAll('input');
            var csrfToken = '';
            for (i = 0; i < inputElems.length; ++i) {
                if (inputElems[i].name === 'csrfmiddlewaretoken') {
                    csrfToken = inputElems[i].value;
                    break;
                }
            }
            return csrfToken;
        }; 
        
        var gtotal = "{{gtotal}}" // django function in string form
        var url = "{% url 'payment' %}"
        const csrf = getCsrf()
        var order_id = "{{order.order_number}}"
        var method = 'PayPal'
        var order_complete_url = "{% url 'order_complete' %}" 

        const paypalButtonsComponent = paypal.Buttons({
            // optional styling for buttons
            // https://developer.paypal.com/docs/checkout/standard/customize/buttons-style-guide/
            style: {
              color: "gold",
              shape: "rect",
              layout: "vertical"
            },

            // set up the transaction
            createOrder: (data, actions) => {
                // pass in any options from the v2 orders create call:
                // https://developer.paypal.com/api/orders/v2/#orders-create-request-body
                const createOrderPayload = {
                    purchase_units: [
                        {
                            amount: {
                                value: gtotal
                            }
                        }
                    ]
                };

                return actions.order.create(createOrderPayload);
            },

            // finalize the transaction
            onApprove: (data, actions) => {
                const captureOrderHandler = (details) => {
                    const payerName = details.payer.name.given_name;
                    console.log('Transaction completed');
                    sendData()

                    function sendData(){
                        fetch(url, {
                            method : "POST",
                            header : {
                                "content-type" : "application/json",
                                "X-CSRFToken" : csrf,
                            },
                            body : JSON.stringify({
                                orderID : order_id,
                                transID : details.id,
                                payment_method : method,
                                status : details.status,
                            })
                        })
                        // here we are agin recieving response back from server and this data will be re-directed to order_complete page
                        .then(response => response.json())
                        .then(data => {
                            window.location.href = order_complete_url + '?order_number=' + data.order_number +'&payment_id=' + data.trans_id // get request to order complete url 
                        })
                    }
                };

                return actions.order.capture().then(captureOrderHandler);
            },

            // handle unrecoverable errors
            onError: (err) => {
                console.error('An error prevented the buyer from checking out with PayPal');
            }
        });

        paypalButtonsComponent
            .render("#paypal-button-container")
            .catch((err) => {
                console.error('PayPal Buttons failed to render');
            });
      </script>