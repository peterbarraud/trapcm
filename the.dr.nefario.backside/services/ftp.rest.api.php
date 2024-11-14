<?php
  require 'chotarest/app.php';
  $restapp = new RestfulApp();
  $restapp->HandleCors();
  $restapp->run();

  // To test this out
  // http://localhost:8089/services/rest.api.php/testrest/booga
  function testrest($param){
    echo "<div style='background-color:#9baedd;color:#723014;font-size:30px;padding:20px;border:5px solid #723014;'>If you called the <code>testrest</code> API and passed <code>" . $param . "</code> as the parameter, then your <b>Rest server</b> is set up good!</div>";
  }

  function getcurrentsystemversion(){
    require_once('objectlayer/trapcmsyscollection.php');
    $trapcmsyscollection = new trapcmsyscollection();
    $trapcmsys = $trapcmsyscollection->getobjectcollection()[0];
    echo json_encode($trapcmsys->version);
  }

  function bumpbuilmajorversion(){
    require_once('objectlayer/trapcmsyscollection.php');
    $trapcmsyscollection = new trapcmsyscollection();
    $trapcmsys = $trapcmsyscollection->getobjectcollection()[0];
    $parts = explode('.',$trapcmsys->version);
    $bumped_major_version_number = intval($parts[0]) + 1;
    $trapcmsys->version = $bumped_major_version_number . '.' . $parts[1];
    $trapcmsys->Save();
    echo json_encode($trapcmsys);
  }

  function bumpbuilminorversion(){
    require_once('objectlayer/trapcmsyscollection.php');
    $trapcmsyscollection = new trapcmsyscollection();
    $trapcmsys = $trapcmsyscollection->getobjectcollection()[0];
    $parts = explode('.',$trapcmsys->version);
    $bumped_minor_version_number = intval($parts[1]) + 1;
    $trapcmsys->version = $parts[0] . '.' . $bumped_minor_version_number;
    $trapcmsys->Save();
    echo json_encode($trapcmsys);
  }

  function setbuilddate(){
    require_once('objectlayer/trapcmsyscollection.php');
    $trapcmsyscollection = new trapcmsyscollection();
    $trapcmsys = $trapcmsyscollection->getobjectcollection()[0];
    $trapcmsys->lastbuild = 'now()';
    $trapcmsys->Save();
    echo json_encode($trapcmsys);
  }


  function console_log($message) {
    $STDERR = fopen("php://stderr", "w");
              fwrite($STDERR, "\n".$message."\n");
              fclose($STDERR);
  }


?>
