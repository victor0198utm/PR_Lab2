# Used protocols:
### TCP:
- HTTP
- FTP (client and server)
- SMTP
- POP3 (using SSL)

## Domain 1: File storage server app and client
The server is offers posibility to connect different users. It has a database for account and file details storage. The details include file description and uploading date.
Note: The server can work with one user at a time. When switching users, server app needs to be restarted.

## Domain 2: Message seding and fetching
Clients for sending messages from a gmail account, using SMTP. Client for getting new messages from a gmail account using POP3.

## Server app
Provides FTP sevices and HTTP endpoints to: 
- register an account;
- add new file record in DB;
- get list of files for a specific user.

## FTP Client app
Has an interface containing:
- user registration and authentication (two in one: if username does not exist, it is registered, and a folder for his files is created; if username exists and passsword is wrong, it is rejected);
- file selection and uploading
- listing of files from the server (of the logged in user);
- file selecting and downloading, one by one;

## Usage:
### FTP & HTTP
On first start of the server app, the database is created.
<br/><image src="/examples/1.png"><br/>
<br/><image src="/examples/2.png"><br/>
The client app can be opened to connect to the server.
<br/><image src="/examples/3.png"><br/>
A new user is added and the FPT services are started. Then, the user is connected to the server through the FTP. After the connection is established, the client app requests the user files. Now, there aren't any.
<br/><image src="/examples/4.png"><br/>
On the server, there is built a folder with the user's username, for his files.
<br/><image src="/examples/5.png"><br/>
The user can select a file from his device and optionally write a description for the file, then upload it on the server.
<br/><image src="/examples/6.png"><br/>
<br/><image src="/examples/7.png"><br/>
<br/><image src="/examples/8.png"><br/>
<br/><image src="/examples/9.png"><br/>
<br/><image src="/examples/12.png"><br/>
To download a file, the user should select one itam from the files list, and click on Download button.
<br/><image src="/examples/10.png"><br/>
And the file is downloaded in the same directory of the client app location.
<br/><image src="/examples/11.png"><br/>

### SMTP & POP3
1. Client for getting the new messages.
Authentication:
<br/><image src="/examples/15.png"><br/>
Clicked on Refresh and got one message:
<br/><image src="/examples/13.png"><br/>
After a while and refreshing again, got one more:
<br/><image src="/examples/14.png"><br/>

2. Client for sending messages.
Autehntication:
<br/><image src="/examples/15.png"><br/>
Write the receiver and message content:
<br/><image src="/examples/16.png"><br/>
The email was received:
<br/><image src="/examples/17.png"><br/>
