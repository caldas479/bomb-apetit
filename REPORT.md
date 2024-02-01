# C18 BombAppetit Project Report
## 1. Introduction

BombAppetit is a system where Users can explore a variety of restaurants and manage the vouchers that they own for each one. They should be able to use or transfer their vouchers to another User of their choosing.

These vouchers will be stored in secure documents, that prevents other User's from accessing a voucher that doesn't belong to them.
The documents will also have the menu for the restaurant protected in a way that allows Users to be certain that it hasn't been tampered with.

Each user can also write a review for a restaurant and read other User's reviews and all reviews are authenticated by the User that wrote them.

For this scenario we agreed to implement a moderate confidentiality and security, since our service is built from trust between the service and the users. This shaped our decisions and the way we utilize our resources, being the key to our implementation.


## 2. Project Development

### 2.1. Secure Document Format

#### 2.1.1. Design

To implement this project we decided to use Python. Despite considering using Java, we opted for Python since we were already familiar with this language when working with Flask and web servers and databases.

An example of our protected data format is this document in json format.
The meal Voucher is protected by the belonging user's Public Key to make sure that only the user has access to it.
The Signature is created by the restaurant Private Key to prove it's integrity.

```plaintext
{
    "restaurantInfo": {
        "owner": "Jane Doe",
        "restaurant": "Burger King",
        "address": "456 Oak Street, Downtown",
        "genre": [
            "American",
            "Fast Food"
        ],
        "menu": [
            {
                "itemName": "Whopper",
                "category": "Burger",
                "description": "Flame-grilled beef patty topped with lettuce, tomato, onion, and mayo.",
                "price": 5.99,
                "currency": "USD"
            },
            {
                "itemName": "Chicken Fries",
                "category": "Chicken",
                "description": "Crispy chicken strips seasoned to perfection.",
                "price": 3.99,
                "currency": "USD"
            },
            {
                "itemName": "Vegetarian Wrap",
                "category": "Vegetarian",
                "description": "Grilled veggies wrapped in a soft tortilla with special sauce.",
                "price": 4.99,
                "currency": "USD"
            }
        ],
        "mealVoucher": "9ae5445606b9ff3a7d59ba1de0f3c65ad607b47da4c6ac4aea74be55248c0c1aac99326f31d53f0f442139e165bf88dd0d2871"
    },
    "signature": "jOIRj7OEML3utF6Ycuxy0QiKVN+Mb2md5hcju7zQONHXQKm+bH308xEkIzSxzrM7C84VpxZq9KGyFfw=="
}
```

Our cryptographic library consists of 3 main functionalitys: `protect`, `check` and `unprotect`.

`protect` as the name says, protects a JSON document by encrypting and adding a digital signature. This digital signature is signed with the restaurant's private key to ensure the integrity of the document. We opted for this considering every restaurant already had a private key, and also a public key that all Users have access to. Because each voucher is suposed to be confidential and available only to the User it belongs to, we need to use this feature.

`check` checks for the integrity and authenticity of the signature in a protected JSON document. This is used everytime a User read a voucher.

`unprotect` removes any protection from a JSON document by decrypting and removing security details.

One of the hardships faced when doing these functionalitys was working with the file paths to the json files. We later altered this implementation and only read the json file once, and then worked with the json object obtained by this, improving the efficiency and overall readability of the code.
#### 2.1.2. Implementation

We used the `cryptography` library in python to make the algorithms that encrypt, decrypt and verify the documents. These files lie in src/security_library. Since the code provided by the teachers of the class was written in Java we couldn't base our work on what we had done in the practical lectures, however, python was not very hard to deal with.

For the API we used Flask with SQLAlchemy to connect to the PostgreSQL Database we used. We used this libraries and frameworks because we were confortable with them.
One challenge faced was enabling https in Flask, as we needed a certification file and a key file. 

For the client we used a library that we weren't familiar but quickly got, `PyInquirer` library, it allowed us to build an easy interactive command line interface. For the client to connect to the API itself we used the `requests` library.

For the database using PostgreSQL was quite the challenge since we had to configure a lot of files to make the ips of every VM work, but after this was all done everything worked quite smoothly.




### 2.2. Infrastructure

#### 2.2.1. Network and Machine Setup

Our built infrastructure consists of 4 Virtual machines.
The VM that runs the Database server is only connected to the Firewall and Gateway VM for improved security, and this FW&GW VM will then connect to the API VM that runs the flask app to make the link to the database.
Finally the Client VM will only be connected to the API VM that runs the application.

We opted for postgres for our database considering it is one of the most popular options for database management systems, and also for the fact that we were familiar with this technology.

For our application, Flask seemed like the only choice due to it's simplicity and flexibility for developing web applications, and even though we didn't develop a web app for this project, doing so would not be too much of a challenge with Flask.

For our CLI, we used the library PyInquirer considering Python was the language we were most confortable with, and it would integrate nicely with our Python application. This way we could avoid mixing different languages in our project.

#### 2.2.2. Server Communication Security

The communication between the Database Server and the Flask application has the following security measures:
- A layer of security in the form of a Firewall and Gateway Virtual Machine that acts as a middle man to prevent the API VM and the DB VM to communicate directly, this simulates a separation between the DMZ and the internal network and gives it another layer of security.
- The Firewall should block any communication to the Database that is not from the FW&GW VM IP address, although the PostgreSQL configuration settings only allow connection from the API VM IP and from itself.
- The API VM will also not allow any https requests that are not destined for the port that the application is running, this makes the API more trustable and less vulnerable to requests from attackers. 
- The flask app will also run on https so both the application and the database have TLS protection when communicating, making all packets encrypted, ensuring that the communication is not readable when sniffing, and so no privileged information is leaked.
- In the PostgreSQL configurations we've also enabled the SSL protocol so that someone sniffing can't see the queries and the values returned by the database server.

In this section we stuck to what we had planned, as we want our service to be secure in a moderate way, prioritizing the availability and the undeniable trust in the service.

### 2.3. Security Challenge

#### 2.3.1. Challenge Overview

With the security challenge our project was introduced to reviews written by Users. These reviews can be read by any User and they must be able to verify it's authenticity.

The vouchers would now be tied to specific Users, with the option of being used or transfered to another User. 

Since each user still only has its own keys, some dynamic key distribution had to be implemented.

#### 2.3.2. Attacker Model

Spoofing --> an atacker could not fullfil his attack considering every communication packet is protected and encrypted by TLS.

Data Tampering --> if the document with the voucher or the review is tampered, our application will handle this with integrity checks.

Replay Attacks --> attackers might capture and replay valid requests to the server to perform unauthorized actions. We relay on timestamps to mitigate these.

#### 2.3.3. Solution Design and Implementation

To handle key distribution, when the user logs in, the server sends him all users' public keys, and the client stores them locally. 

To make sure the user can verify that the reviews were authentic:
- When a user reviews a restaurant, the document with the review is signed by the author.
- When a user wants to see the reviews from a restaurant, the client side will verify all review signatures with the respective author's public key.

This logic could only be implemented due to our key distribution mechanism, as before the Security Challenge, the users didn't know other's public keys.

This seemed the best strategy to us as our application doesn't require full confidentiality but more availability and trust and that was our thinking throughout the whole design.

When the vouchers were transferred we also implemented a security feature that allows the server to check the signature of the user that sent the voucher, and then updates the database.

To further secure our application, every request and response sends a timestamp and that timestamp is verified each time. The time window for the timestamp to be valid is 2 seconds, an arbirtrary value that was chosen but makes sure to prevent any sort of replay attack.

## 3. Conclusion

We managed to ensure Integrity of every Restaurant document with a Signature generated with the Restaurant's `Private key`.
The vouchers were sucessfully protected with the belonging User's `Public key` to ensure that only they can use it or transfer it.

Even though we believe our project is very sucessful, there is always room for improvements. We could have made Exceptions for various problems that can occur. The Gateway between the API VM and the Database VM could've been setup with a firewall, but despite our best efforts in doing so we, couldn't accomplish due to the lack of time and how we had to shift our attention to more serious issues. The reviews could've been written in the document itself, this however always comes with an efficiency cost so it's up for the developers to know what's best.

This project, despite the many difficultys, showed itself to be very rewarding and valuable.
For the first time we found ourselves working with databases, networks, security and web applications, all for the same project, which made us strategize and grow as both students and programmers.


----
END OF REPORT
