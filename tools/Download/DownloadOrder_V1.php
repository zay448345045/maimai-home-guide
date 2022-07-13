<?php

error_reporting(1);

if ($_POST["ID"])

{

    $compressed = base64_encode(gzdeflate("game_id=".$_POST["ID"]."&ver=".$_POST["VERSION"]."&serial=A63E01B1628", -1, ZLIB_ENCODING_DEFLATE));

    //print($compressed);

    // use key 'http' even if you send the request to https://...

    $options = array(

        'http' => array(

            'header'  => "Pragma: DFI",

            'method'  => 'POST',

            'content' => $compressed

        )

    );

    $context  = stream_context_create($options);

    $result = file_get_contents('http://naominet.jp/sys/servlet/DownloadOrder', false, $context);

    if ($result === FALSE) { exit("error dl\n"); /* Handle error */ }

    //print($result);

    $response = gzuncompress(base64_decode($result));

    print($response);

}

?>

<title>SEGA DOWNLOADORDER</title>

<b><form action="/index.php" method="post">

GAME ID:<input type="text" name="ID">

GAME VERSION:<input type="text" name="VERSION">

<input type="SUBMIT" value="SUBMIT"><br>

</form></b>