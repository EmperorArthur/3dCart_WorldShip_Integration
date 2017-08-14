# A set of tools to integrate 3dCart with UPS Worldship
Provides an automatic link betwen 3dCart and UPS Wordlship.

Copyright Arthur Moore GPL V3 2017
Feel free to contact me to obtain the code under other license terms

# Background
UPS Wordlship is a program to handle creating shipping labels by and for UPS.
3dCart is an online shopping cart platform.

## Current Situation
3dCart contains a "solution" to integrate with UPS Worldship, but that requires manually exporting a csv file that UPS Worldship reads to see order information.
Every time the shipper has processed all the orders in that file they have to manually export a new file, and hope that Worldship likes them.

## 3dCart
3dCart provides a [REST API](https://apirest.3dcart.com/Help).
However, there is no easy way for clients to access it.
Instead, there is a multi step process involving web apps, API keys, and insecurity.

To access the REST API, developers must create a "web app" via https://devportal.3dcart.com \*
Once a developer creates an account at that site (seperate from their store account), they then must create the "app".
From there they need to select what use APIs the "app" will have access to, and put in a URL for the site to register itself at.
In general, all the URL needs to be is a good page served by a known ip, though fully automating the process requires a page that will capture POST requests.
The IP address of the site goes in the whitelist.
Don't worry, as a developer you can change the permissions of your "app" without any user invervention.\*\*
Finally, the developer gives the "app's" public key to the users.

In order to use a "web app", a 3dCart user goes to the `Modules` section of their store's admin page.
They then find the `REST API` module and choose `change settings`.
From there, they click `add`, and enter the public key of the app.

To use the REST API, developers can follow the directions [here](https://apirest.3dcart.com/Help).  Though most of the APIs on that help page seem to offer examples, the code is actually left blank.  Here is a quick and dirty usage guide to the 3dCart REST API.

* The API is accessed via `https://apirest.3dcart.com/3dCartWebAPI/v1/...`
* The following HTTP Headers are MANDATORY:  `SecureUrl`, `PrivateKey`, `Token`
* SecureUrl is taken from 3dCart Admin -> General -> Store Settings -> Secure URL
* PrivateKey is from the "app" page at the [developer site](https://devportal.3dcart.com).
* Token is from the "app" page at the [developer site](https://devportal.3dcart.com).


\* Note:  That website has major issues:
* Putting a '%' in the password will be accepted at creation, but users can not log in with that password.  Possible vulnerability?!
* 3 incorrect logins locks the account, and the password must be reset.  Easy denial of service target!
* Password reset E-mails are never sent.  Once a user is locked out, they would have to phone support to get back in!

\*\*  Yes, I know this is also highly insecure.

## UPS Worldship
UPS Worldship works using ODBC drivers.  These are database backends.  Used for accessing things like MySQL.  The 3dCart solution requires setting up a backend that reads and treats a CSV file as a database.  It works, but is inneficient and frequently breaks.  Especially when trying to use this process on multiple computers.

UPS Worldship does NOT natively support any sort of REST API or other means of obtaining data than via an ODBC driver.

## The solution
Unfortunately, writing an ODBC driver is difficult.  Fortunately codeape from [stackoverflow](https://stackoverflow.com/questions/335008/creating-a-custom-odbc-driver) had an idea, and posted some example code.  The idea is to use an ODBC driver for PostgreSQL, and use a Python program to pretent to be a Postgres Server.

After looking at the example code and the [protocol information](https://www.postgresql.org/docs/8.1/static/protocol.html), I then wrote my own server implementation.  The current sever only responds to `SELECT` queries with a fixed response.  It just says "Done" when given any other command.

## TODO:
This will then be combined with a Python REST client.
The absolute minimum commands needed to support bridging the application and the shopping cart will be handled.
