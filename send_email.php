<?php
if ($_POST) {
    $name = htmlspecialchars($_POST['user_name']);
    $email = htmlspecialchars($_POST['user_email']);
    $message = htmlspecialchars($_POST['message']);
    
    $to = "akshatjain9989@gmail.com";
    $subject = "Portfolio Contact Form - " . $name;
    $body = "Name: $name\nEmail: $email\n\nMessage:\n$message";
    $headers = "From: $email\r\nReply-To: $email";
    
    if (mail($to, $subject, $body, $headers)) {
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['success' => false]);
    }
}
?>