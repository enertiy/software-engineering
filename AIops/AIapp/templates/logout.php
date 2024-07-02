<?php
// 假设您已经连接到数据库，并且有一个名为$userId的变量，它包含了当前登录用户的ID
$username = '错误'; // 如果查询失败，将显示此默认用户名

// 准备SQL查询，从aiapp_user表中获取用户名
$query = "SELECT username FROM aiapp_user"; // 使用预处理语句来防止SQL注入

// 预处理SQL语句
if ($stmt = $mysqli->prepare($query)) {
    // 绑定参数
    $stmt->bind_param("i", $userId);

    // 执行查询
    $stmt->execute();

    // 绑定结果变量
    $stmt->bind_result($username);

    // 获取查询结果
    $stmt->fetch();

    // 关闭语句
    $stmt->close();
}

// 使用查询结果中的用户名
echo "<div class=\"text-center p-3 bg-light rounded\">
          < img src=\"https://placehold.co/110x110\" class=\"rounded-circle p-1 shadow mb-3\" width=\"120\" height=\"120\"
            alt=\"\">
          <h5 class=\"user-name mb-0 fw-bold\">".htmlspecialchars($username)."</h5>
          <p class=\"mb-0\">Administrator</p >
      </div>";
?>