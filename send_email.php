<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = htmlspecialchars($_POST['user_name'] ?? '');
    $email = htmlspecialchars($_POST['user_email'] ?? '');
    $message = htmlspecialchars($_POST['message'] ?? '');
    
    if (empty($name) || empty($email) || empty($message)) {
        echo json_encode(['success' => false, 'error' => 'All fields required']);
        exit;
    }
    
    $to = 'akshatjain9989@gmail.com';
    $subject = 'Portfolio Contact - ' . $name;
    $body = "Name: $name\nEmail: $email\n\nMessage:\n$message";
    $headers = "From: $email\r\nReply-To: $email\r\nX-Mailer: PHP/" . phpversion();
    
    if (mail($to, $subject, $body, $headers)) {
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['success' => false, 'error' => 'Failed to send']);
    }
} else {
    echo json_encode(['success' => false, 'error' => 'Invalid request']);
}
?>