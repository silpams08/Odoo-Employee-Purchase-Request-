# Odoo-Employee-Purchase-Request-
Three Type of users,

 1. Employee
 2. Manager
 3. Internal
 
* The user will redirected to the Employee/Manager portal after login based on their user type. 
* The employees can request for a product purchase.
* The products and qunatity for each employee is restricted based on the employee configuration.
* There is an option to configure custom tax for each employee in employee profile.
* The tax will be taken from the profile if the employee have custom tax, else it will be calculated globally.
* The employee can select product variants and based on the variants the price will be changed.
* if there is multiple supplier for the product, select the supplier from the list of suppliers displayed.
* When the Request order is created the state will be in Draft
* A mail send to the manager user upon creating new request.

* Once the employee requested for the product, the Manager will check the request and can approve/reject the request.
* The state will be changed to Approve/Reject based on the managers action.
* A Mail notification will be send once the manager approve/reject the request.
* If the manager rejects the request, then the employee can request for any product only on next month.
* If the Manager approves the request the employee can buy the product, Which will create a purchase order in the backend.
* The state will be changed to Purchase Inprogress.

* Internal user will be the one approving the purchase request, and receives the product.
* When the product is received by the internal user, the state will be changed to Ready to Pickup.
* A notification mail will be send to the employee when it is ready to pickup.
* Once the product is picked by the employee, the request will be closed.

