using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
using System;
using System.Net;
using System.Net.Mail;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;

public class SendEmail : MonoBehaviour
{
    public InputField addressField;
    public InputField subjectField;
    public InputField bodyField;

    private string address;
    private string subject;
    private string body;

    public void OnSubmit()
    {
        address = addressField.text;
        subject = subjectField.text;
        body = bodyField.text;

        MailMessage mail = new MailMessage();
        mail.From = new MailAddress("neurotechar@gmail.com");
        mail.To.Add(address);
        mail.Subject = subject;
        mail.Body = body;
        // you can use others too.
        SmtpClient smtpServer = new SmtpClient("smtp.gmail.com");
        smtpServer.Port = 587;
        smtpServer.Credentials = new System.Net.NetworkCredential("neurotechar@gmail.com", "building21!") as ICredentialsByHost;
        smtpServer.EnableSsl = true;
        ServicePointManager.ServerCertificateValidationCallback =
            delegate(object s, X509Certificate certificate, X509Chain chain, SslPolicyErrors sslPolicyErrors)
            { return true; };
        smtpServer.Send(mail);

        addressField.text = "";
        subjectField.text = "";
        bodyField.text = "";

    }
}
