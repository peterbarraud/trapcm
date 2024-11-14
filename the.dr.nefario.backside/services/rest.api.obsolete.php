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

  function console_log($message) {
    $STDERR = fopen("php://stderr", "w");
              fwrite($STDERR, "\n".$message."\n");
              fclose($STDERR);
  }



  function __deletequestionbyid($question_id){
    require_once('objectlayer/question.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/namevalue.php');
    $answercollection = new answercollection(new NameValue('question_id','=',$question_id));
    $answer = $answercollection->getobjectcollection()[0];
    $answer->Delete();
    $choicecollection = new choicecollection(new NameValue('question_id','=',$question_id));
    foreach($choicecollection->getobjectcollection() as $choice) {
      $choice->Delete();
    }
    $question = new question($question_id);
    $question->Delete();

    return $question_id;

  }

  function __highlighter($whattohighlight){
    $highligher = "<span style='color:Tomato;font-weight:bold;font-size:22px'>{placeholder}</span>";
    return str_replace('{placeholder}',$whattohighlight,$highligher);
  }

  // function makedummyquestions($topic_id,$number_of_questions,$question_type){
  //   echo $topic_id . '-' . $number_of_questions . '-' . $question_type . '<br>';
  //   $topic_id = explode('=',$topic_id)[1];
  //   $number_of_questions = explode('=',$number_of_questions)[1];
  //   $question_type = explode('=',$question_type)[1];
  //   echo $topic_id . '-' . $number_of_questions . '-' . $question_type . '<br>';
  // }

  // $question_type = either 1 (MCQ) or 3 (Long form)

  function savequestion($question_id){
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
      $json = file_get_contents('php://input');
      $data = json_decode($json);
      require_once('objectlayer/question.php');
      require_once('objectlayer/namevalue.php');
      require_once('objectlayer/answercollection.php');
      require_once('objectlayer/choice.php');
      require_once('objectlayer/choicecollection.php');
      $question = new question($question_id);
      // so the method we're using is to first check if the quetion exists (this is an update)
      // so every time we recreate
      $question->q_type_id = $data->questionTypeID;
      $question->topic_id = $data->topicID;
      $question->is_jee_advanced = $data->advanced;
      if (isset($data->description)){
        $question->description = $data->description;
      } else {
        if ($data->imageStr != null){
          $question->filestr = $data->imageStr;
        }
      }
      $question->q_src_id = $data->source;
      $question->Save();
      $answer = null;
      $answercollection = new answercollection(new NameValue('question_id','=',$question->id));
      if ($answercollection->length == 1){  #existing answer for existing question
        $answer = $answercollection->getobjectcollection()[0];
      } else { #new answer for new question
        require_once('objectlayer/answer.php');
        $answer = new answer();
      }
      
      $answer->url = $data->answerURL;
      $answer->question_id = $question->id;
      if (isset($data->answerdescription)){
        $answer->description = $data->answerdescription;
      } else {
        $answer->filestr = $data->answerImageStr;
      }
      $answer->Save();

      // if this is a question update, let's first delete existing chioces
      // but why not just re-use the choices we have
      // well, there'll be a problem if the number of choice change - MCQ to TF, for example
      $choicecollection = new choicecollection(new NameValue('question_id','=',$question->id));
      foreach($choicecollection->getobjectcollection() as $choice) {
        $choice->Delete();
      }
      
      foreach($data->choices as $choicedata) {
        $choice = new choice();
        $choice->question_id = $question->id;
        $choice->correct_ans = $choicedata->iscorrect;
        if (isset($choicedata->description)){
          $choice->description = $choicedata->description;
        } else{
          if ($choicedata->imageStr != null){
            $choice->filestr = $choicedata->imageStr;
          }
        }
        $choice->Save();
      }
      echo json_encode($question->id);
    }
  }

  // offset starts at 1
  // offset = 1 => last item
  // offset = 2 => second last item
  // offset = 3 => third last item
  // and so on...
  function getrecentquestion($offset){
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/questiontype.php');
    require_once('objectlayer/namevalue.php');

    $limit = $offset - 1 . ',1';
    $questioncollection = new questioncollection(null, $sortby='id', $sortdirection='desc', $limit=$limit);
    if ($questioncollection->length > 0){
      $question = $questioncollection->getobjectcollection()[0];
      $question->questiontype = new questiontype($question->q_type_id);
      $answercollection = new answercollection(new NameValue('question_id','=',$question->id));
      $question->answer = $answercollection->getobjectcollection()[0];
      $choicecollection = new choicecollection(new NameValue('question_id','=',$question->id));
      $question->choices = $choicecollection->getobjectcollection();
      echo json_encode($question);
    } else {
      $question = (object)[];
      $question->id = -1;
      echo json_encode($question);
    }
  }

  function __getquestionbyid($question_id){
    require_once('objectlayer/question.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/namevalue.php');
    require_once('objectlayer/questiontype.php');
    $question = new question($question_id);
    $answercollection = new answercollection(new NameValue('question_id','=',$question_id));
    $question->answer = $answercollection->getobjectcollection()[0];
    $choicecollection = new choicecollection(new NameValue('question_id','=',$question_id));
    $question->choices = $choicecollection->getobjectcollection();
    $question->questiontype = new questiontype($question->q_type_id);
    return $question;
  }

  function getquestionbyid($question_id){
    echo json_encode(__getquestionbyid($question_id));
  }

  function gettopicandsubjectbytopicyid($topic_id){
    require_once('objectlayer/topic.php');
    require_once('objectlayer/subject.php');
    $retval = array();
    $topic = new topic($topic_id);
    $retval['topic'] = $topic;
    $subject = new subject($topic->subject_id);
    $retval['subject'] = $subject;
    echo json_encode($retval);
  }

  function getattemptedquestion($offset){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    $limit = $offset - 1 . ',1';
    $laststudentattempted = (new studentattemptedcollection(null,"timeattempted_ts",'desc',$limit))->getobjectcollection()[0];
    // $student_id = $questionsattempted[]
    $lastattemptedquestion = __getquestionbyid($laststudentattempted->question_id);
    $lastattemptedquestion->doubttype = $laststudentattempted->doubttype;
    echo json_encode($lastattemptedquestion);
  }

  function deletequestionbyid($question_id){
    echo json_encode(__deletequestionbyid($question_id));

  }

  // this function increments the appuser->wenttooldcounter every time any user goes to the old TraPCM from the sign-in page
  function oldtrapcmused($appuser_id){
    require_once('objectlayer/appuser.php');
    $appuser = new appuser($appuser_id);
    $appuser->oldtrapcmused += 1;
    $appuser->Save();
    echo json_encode($appuser->oldtrapcmused);
  }

  function validateuser($username, $password){
    require_once('objectlayer/appusercollection.php');
    require_once('objectlayer/trapcmsys.php');
    require_once('objectlayer/namevalue.php');
    $retval = array();
    $filter = array(new NameValue('email', '=', $username), new NameValue('pwd', '=', $password));
    $users = new appusercollection($filter);
    if ($users->length == 1){
      $user = $users->getobjectcollection()[0];
      // if this is a valid user then check for app status
      $retval["id"] = $user->id;
      $retval["email"] = $user->email;
      $retval["firstname"] = $user->firstname;
      $retval["lastname"] = $user->lastname;
      $retval["role"] = $user->role;
      $retval["isvaliduser"] = TRUE;
      $trapcmsys = new trapcmsys(1);
      if (strtotime($trapcmsys->lastbuild) > strtotime($user->lastapprefresh)){
        $retval["updatesrequired"] = TRUE;
      } else {
        $retval["updatesrequired"] = FALSE;
      }
    } else {
      $retval["isvaliduser"] = FALSE;
      $users = new appusercollection(new NameValue('email', '=', $username));
      if ($users->length == 1){
        $retval["isvalidemail"] = TRUE;
      } else {
        $retval["isvalidemail"] = FALSE;
      }
    }
    echo json_encode($retval);
  }

  function updateapprefreshdata($student_id, $timestr){
    require_once('objectlayer/appuser.php');
    $user = new appuser($student_id);
    $user->lastapprefresh = $timestr;
    $user->Save();
    echo json_encode($user);
  }


  function obsolete_getappuserbyid($id) {
    require_once('objectlayer/appuser.php');
    $user = new appuser($id);
    echo json_encode($user);
  }

  function obsolete_unansweredquestionsreport($student_id){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');

    $attempted_questionid_list = array();
    $attemptedquestions = new studentattemptedcollection(new NameValue('student_id', '=', $student_id));
    foreach($attemptedquestions->getobjectcollection() as $attemptedquestion){
      array_push($attempted_questionid_list, $attemptedquestion->question_id);
    }
    $retval = array();
    $subjects = new subjectcollection();
    foreach($subjects->getobjectcollection() as $subject){
      
    }
    $topics = new topiccollection();
    foreach($topics->getobjectcollection() as $topic){
      $filter = array();
      array_push($filter, new NameValue('topic_id', '=', $topic->id));
      array_push($filter, new NameValue('id', 'not in', $attempted_questionid_list));
      $questions = new questioncollection($filter);
      if ($questions->length){
        $topic->questioncount = $questions->length;
        array_push($retval, $topic);
      }
    }
    echo json_encode($retval);

  }

  function getallsubjectsandtopics(){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/namevalue.php');

    $attemptedquestions_array = array();
    $subjects = new subjectcollection();
    $retval = array();
    // array that we'll add to the subjects object
    foreach($subjects->getobjectcollection() as $subject) {
      $subject->topics = array();
      $topics = new topiccollection(new NameValue('subject_id', '=', $subject->id));
      $subject->topics = $topics->getobjectcollection();
      array_push($retval, $subject);
    }
    echo json_encode($retval);
  }

  function getquestionsources(){
    require_once('objectlayer/sourcecollection.php');
    $sources = new sourcecollection();
    echo json_encode($sources->getobjectcollection());
  }


  function getsubjectsandtopicsunanswered($student_id,$test_name){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/namevalue.php');

    $attemptedquestions_array = array();
    $attemptedquestions = new studentattemptedcollection(new NameValue('student_id', '=', $student_id));
    foreach($attemptedquestions->getobjectcollection() as $attemptedquestion){
      array_push($attemptedquestions_array, $attemptedquestion->question_id);
    }
    $subjects = new subjectcollection();
    $retval = array();
    // array that we'll add to the subjects object
    foreach($subjects->getobjectcollection() as $subject) {
      $subject->topics = array();
      $filter = array();
      array_push($filter, new NameValue('subject_id', '=', $subject->id));
      array_push($filter, new NameValue('show_topic', '=', 1));
      array_push($filter, new NameValue('test_name', '=', $test_name));
      $topics = new topiccollection($filter);
      foreach($topics->getobjectcollection() as $topic){
        $filter = array();
        array_push($filter, new NameValue('topic_id', '=', $topic->id));
        if (count($attemptedquestions_array) > 0){
          array_push($filter, new NameValue('id', 'not in', $attemptedquestions_array));
        }
        $questions = new questioncollection($filter);
        if ($questions->length > 0){
          array_push($subject->topics, $topic);
        }
      }
      if (count($subject->topics) > 0){
        array_push($retval, $subject);
      }
    }
    echo json_encode($retval);
  }

  function getsubjectsandtopicsdoubts($student_id){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/namevalue.php');

    $doubtquestions_array = array();
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('savefordoubt', '=', '1'));
    $doubtquestions = new studentattemptedcollection($filter);
    // if there are no doubt questions, simply return an empty array
    if (sizeof($doubtquestions->getobjectcollection()) == 0){
      echo json_encode(array());

    } else {
      foreach($doubtquestions->getobjectcollection() as $doubtquestion){
        array_push($doubtquestions_array, $doubtquestion->question_id);
      }
      $subjects = new subjectcollection();
      $retval = array();
      // array that we'll add to the subjects object
      foreach($subjects->getobjectcollection() as $subject) {
        $subject->topics = array();
        $topics = new topiccollection(new NameValue('subject_id', '=', $subject->id));
        foreach($topics->getobjectcollection() as $topic){
          $filter = array();
          array_push($filter, new NameValue('topic_id', '=', $topic->id));
          if (count($doubtquestions_array) > 0){
            array_push($filter, new NameValue('id', 'in', $doubtquestions_array));
          }
          $questions = new questioncollection($filter);
          if ($questions->length > 0){
            array_push($subject->topics, $topic);
          }
        }
        if (count($subject->topics) > 0){
          array_push($retval, $subject);
        }
      }
      echo json_encode($retval);
    }
    
  }

  function getsubjectsandtopicsnotes($student_id){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/namevalue.php');

    $notequestions_array = array();
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('isnote', '=', '1'));
    $notequestions = new studentattemptedcollection($filter);
    // if there are no note questions, simply return an empty array
    if (sizeof($notequestions->getobjectcollection()) == 0){
      echo json_encode(array());

    } else {
      foreach($notequestions->getobjectcollection() as $notequestion){
        array_push($notequestions_array, $notequestion->question_id);
      }
      $subjects = new subjectcollection();
      $retval = array();
      // array that we'll add to the subjects object
      foreach($subjects->getobjectcollection() as $subject) {
        $subject->topics = array();
        $topics = new topiccollection(new NameValue('subject_id', '=', $subject->id));
        foreach($topics->getobjectcollection() as $topic){
          $filter = array();
          array_push($filter, new NameValue('topic_id', '=', $topic->id));
          if (count($notequestions_array) > 0){
            array_push($filter, new NameValue('id', 'in', $notequestions_array));
          }
          $questions = new questioncollection($filter);
          if ($questions->length > 0){
            array_push($subject->topics, $topic);
          }
        }
        if (count($subject->topics) > 0){
          array_push($retval, $subject);
        }
      }
      echo json_encode($retval);
    }
    
  }



  // this method is for checking purposes
  // show = 1 - Only get show topics
  // show = 0 - Only get hidden topics
  // all      - Get all topics
  function obsolete_getalltopicsbyvisibility($show){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/namevalue.php');

    $subjects = new subjectcollection();
    // array that we'll add to the subjects object
    foreach($subjects->getobjectcollection() as $subject) {
      if ($show == '1'){
        $topics = new topiccollection(array(new NameValue('subject_id', '=', $subject->id),new NameValue('show_topic', '=', 1)));
      } else if ($show == '0'){
        $topics = new topiccollection(array(new NameValue('subject_id', '=', $subject->id),new NameValue('show_topic', '<>', 1)));
      } else{
        $topics = new topiccollection(new NameValue('subject_id', '=', $subject->id));
      }
      
      $subject->topics = $topics;
    }
    echo json_encode($subjects);
  }

  function getquestiontypes(){
    require_once('objectlayer/questiontypecollection.php');
    $questiontypecollection = new questiontypecollection();
    $retval = array();
    foreach($questiontypecollection->getobjectcollection() as $questiontype) {
      $retval[$questiontype->name] = $questiontype->id;
    }    
    echo json_encode($retval);
  }

  function __getAttemptedQuestionsArray($student_id){
    $attemptedquestions = new studentattemptedcollection(new NameValue('student_id', '=', $student_id));
    $attemptedquestions_array = array();
    
    foreach($attemptedquestions->getobjectcollection() as $attemptedquestion) {
      array_push($attemptedquestions_array,$attemptedquestion->question_id);
    }
    return $attemptedquestions_array;
  }

  function __getDoubtQuestionsDetails($student_id){
    $filter = array();
    $retval = array();
    array_push($filter,new NameValue('student_id', '=', $student_id));
    array_push($filter,new NameValue('savefordoubt', '=', '1'));
    $doubtquestions = new studentattemptedcollection($filter);
    $doubtquestions_array = array();
    $doubtquestions_types = array();
    foreach($doubtquestions->getobjectcollection() as $doubtquestion) {
      array_push($doubtquestions_array,$doubtquestion->question_id);
      $doubtquestions_types[$doubtquestion->question_id] = $doubtquestion->doubttype;
    }
    $retval['doubtquestions'] = $doubtquestions_array;
    $retval['doubtquestionsTypes'] = $doubtquestions_types;
    return $retval;
  }

  function __getNoteQuestionsArray($student_id){
    $filter = array();
    array_push($filter,new NameValue('student_id', '=', $student_id));
    array_push($filter,new NameValue('isnote', '=', '1'));
    $notequestions = new studentattemptedcollection($filter);
    $notequestions_array = array();
    
    foreach($notequestions->getobjectcollection() as $notequestion) {
      array_push($notequestions_array,$notequestion->question_id);
    }
    return $notequestions_array;
  }

  function __getTestTopicsArray($test_id){
    $topicid_array = array();
    $testtopics = new testtopiccollection(new NameValue('test_id', '=', $test_id));
    foreach($testtopics->getobjectcollection() as $testtopic){
      array_push($topicid_array, $testtopic->topic_id);
    }
    return $topicid_array;
  }

  function gettestquestions($student_id,$test_id){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/topic.php');
    require_once('objectlayer/testtopiccollection.php');
    require_once('objectlayer/test.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questiontype.php');
    require_once('objectlayer/namevalue.php');

    // instead of bringing subjects only for the topics that we want, let's just pull in all the subjects
    // there will never be that many subjects anyway
    $subjects = new subjectcollection();
    // let's put the subjects into the returnable array
    foreach($subjects->getobjectcollection() as $subject){
      // for each subject, let's create a questions array
      // into which we will push questions one at a time 
      $subject->questions = array();
    }

    $test = new test($test_id);
    $testtopics = new testtopiccollection(new NameValue('test_id', '=', $test_id));
    $attemptedquestions_array = __getAttemptedQuestionsArray($student_id);

    
    foreach($testtopics->getobjectcollection() as $testtopic){
      $filter = array();
      array_push($filter,new NameValue('topic_id', '=', $testtopic->topic_id));
      array_push($filter,new NameValue('id', 'not in', $attemptedquestions_array));
      $questions = new questioncollection($filter,null,null,$test->questionspertopic);
      foreach($questions->getobjectcollection() as $question) {
        $question->questiontype = new questiontype($question->q_type_id);
        $choices = new choicecollection(new NameValue('question_id', '=', $question->id));
        $question->choices = $choices->getobjectcollection();
        $answer = new answercollection(new NameValue('question_id', '=', $question->id));
        $question->answer = $answer->getobjectcollection()[0];  // since there'll always be one and only one answer
        // now find the subject that this question belongs to (via the topic id)
        $topic = new topic($testtopic->topic_id);
        foreach($subjects->getobjectcollection() as $subject){
          if ($subject->id == $topic->subject_id){
            array_push($subject->questions,$question);
          }
        }
      }
    }
    // an extra step to only send back subject objects which have at least one question
    $retval = array();
    foreach($subjects->getobjectcollection() as $subject){
      if (sizeof($subject->questions) > 0){
        shuffle($subject->questions);
        array_push($retval,$subject);
      }
    }
    echo json_encode($retval);
  }


  // returns the questionaire for either jee or cbse
  // which it return for depends on the topic list
  // because questions are not divided out the test type (jee or cbse)
  // the topics are divided out
  function getquestions($student_id,$topicid_list){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    // require_once('objectlayer/topic.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questiontype.php');
    require_once('objectlayer/namevalue.php');

    
    // instead of bringing subjects only for the topics that we want, let's just pull in all the subjects
    // there will never be many subjects anyway
    $subjects = new subjectcollection();
    // let's put the subjects into the returnable array
    foreach($subjects->getobjectcollection() as $subject){
      // for each subject, let's create a questions array
      // into which we will push questions one at a time 
      $subject->questions = array();
    }

    // get the topics for the array of topics IDs (from client)
    $topics = new topiccollection(new NameValue('id', 'in', explode(",",$topicid_list)));

    $attemptedquestions_array = __getAttemptedQuestionsArray($student_id);
    
    foreach($topics->getobjectcollection() as $topic){
      $filter = array();
      array_push($filter,new NameValue('topic_id', '=', $topic->id));
      array_push($filter,new NameValue('id', 'not in', $attemptedquestions_array));
      // VERY IMPORTANT
      // For now, we aren't returning JEE Adv questions
      array_push($filter,new NameValue('is_jee_advanced', '!=', "1"));
      // we are going to get a fixed number of questions/topic based on the following
      $limit = ceil(5/$topics->length);
      // if number of topics =:
      // 1, then get limit = 10/1 - So, 10 questions will be got
      // if 2, then 5 questions per topic will be got
      // What happens if topics > 1
      // then "always", 1 question per topic will be got - we want this. Since we want at least one question for a topic
      // the good part is that this way, we will have a pretty even spread of quesitons
      // Why sort-by rand():
      // This will return the question in a random order.
      // What mySQL does is that it first randomizes all the rows in the from clause and then returns the number of rows based on the limit
      $questions = new questioncollection($filter, "rand()", null, $limit);
      foreach($questions->getobjectcollection() as $question) {
        $question->questiontype = new questiontype($question->q_type_id);
        $choices = new choicecollection(new NameValue('question_id', '=', $question->id));
        $question->choices = $choices->getobjectcollection();
        $answer = new answercollection(new NameValue('question_id', '=', $question->id));
        $question->answer = $answer->getobjectcollection()[0];  // since there'll always be one and only one answer
        // now find the subject that this question belongs to (via the topic id)
        foreach($subjects->getobjectcollection() as $subject){
          if ($subject->id == $topic->subject_id){
            array_push($subject->questions,$question);
            break;
          }
        }
      }
    }
    // an extra step to only send back subject objects which have at least one question
    $retval = array();
    foreach($subjects->getobjectcollection() as $subject){
      if (sizeof($subject->questions) > 0){
        shuffle($subject->questions);
        array_push($retval,$subject);
      }
    }
    echo json_encode($retval);
  }

  function getdoubtquestions($student_id,$topicid_list){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/studentattemptedcollection.php'); // used in __getDoubtQuestionsArray
    require_once('objectlayer/questiontype.php');
    require_once('objectlayer/namevalue.php');

    
    // instead of bringing subjects only for the topics that we want, let's just pull in all the subjects
    // there will never be many subjects anyway
    $subjects = new subjectcollection();
    // let's put the subjects into the returnable array
    foreach($subjects->getobjectcollection() as $subject){
      // for each subject, let's create a questions array
      // into which we will push questions one at a time 
      $subject->questions = array();
    }

    // get the topics for the array of topics IDs (from client)
    $topics = new topiccollection(new NameValue('id', 'in', explode(",",$topicid_list)));

    $doubtQuestionsDetails = __getDoubtQuestionsDetails($student_id);
    $doubtquestionIDs = $doubtQuestionsDetails['doubtquestions'];
    $doubtquestionsTypes = $doubtQuestionsDetails['doubtquestionsTypes'];
    if (sizeof($doubtquestionIDs)){
      foreach($topics->getobjectcollection() as $topic){
        $filter = array();
        array_push($filter,new NameValue('topic_id', '=', $topic->id));
        array_push($filter,new NameValue('id', 'in', $doubtquestionIDs));
        $questions = new questioncollection($filter);
        foreach($questions->getobjectcollection() as $question) {
          // we are going to explicitly set savefordoubt to 1
          // for all questions that have this in the studentattempted table
          $question->savefordoubt = '1';
          $question->questiontype = new questiontype($question->q_type_id);
          $question->doubttype = $doubtquestionsTypes[$question->id];
          $choices = new choicecollection(new NameValue('question_id', '=', $question->id));
          $question->choices = $choices->getobjectcollection();
          $answer = new answercollection(new NameValue('question_id', '=', $question->id));
          $question->answer = $answer->getobjectcollection()[0];  // since there'll always be one and only one answer
          // now find the subject that this question belongs to (via the topic id)
          foreach($subjects->getobjectcollection() as $subject){
            if ($subject->id == $topic->subject_id){
              array_push($subject->questions,$question);
              break;
            }
          }
        }
      }
    }
    // an extra step to only send back subject objects which have at least one question
    $retval = array();
    foreach($subjects->getobjectcollection() as $subject){
      if (sizeof($subject->questions) > 0){
        array_push($retval,$subject);
      }
    }
    echo json_encode($retval);

  }

  function getnotequestions($student_id,$topicid_list){
    require_once('objectlayer/subjectcollection.php');
    require_once('objectlayer/topiccollection.php');
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questiontype.php');
    require_once('objectlayer/namevalue.php');

    
    // instead of bringing subjects only for the topics that we want, let's just pull in all the subjects
    // there will never be many subjects anyway
    $subjects = new subjectcollection();
    // let's put the subjects into the returnable array
    foreach($subjects->getobjectcollection() as $subject){
      // for each subject, let's create a questions array
      // into which we will push questions one at a time 
      $subject->questions = array();
    }

    // get the topics for the array of topics IDs (from client)
    $topics = new topiccollection(new NameValue('id', 'in', explode(",",$topicid_list)));

    $notequestions_array = __getNoteQuestionsArray($student_id);
    
    foreach($topics->getobjectcollection() as $topic){
      $filter = array();
      array_push($filter,new NameValue('topic_id', '=', $topic->id));
      array_push($filter,new NameValue('id', 'in', $notequestions_array));
      $questions = new questioncollection($filter);
      foreach($questions->getobjectcollection() as $question) {
        $question->questiontype = new questiontype($question->q_type_id);
        $choices = new choicecollection(new NameValue('question_id', '=', $question->id));
        $question->choices = $choices->getobjectcollection();
        $answer = new answercollection(new NameValue('question_id', '=', $question->id));
        $question->answer = $answer->getobjectcollection()[0];  // since there'll always be one and only one answer
        // now find the subject that this question belongs to (via the topic id)
        foreach($subjects->getobjectcollection() as $subject){
          if ($subject->id == $topic->subject_id){
            array_push($subject->questions,$question);
            break;
          }
        }
      }
    }
    // an extra step to only send back subject objects which have at least one question
    $retval = array();
    foreach($subjects->getobjectcollection() as $subject){
      if (sizeof($subject->questions) > 0){
        array_push($retval,$subject);
      }
    }
    echo json_encode($retval);    
  }

  function __obsolete_getdoubtquestionsbytopics($student_id, $topicid_list){
    $topicid_array = explode(",",$topicid_list);
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questiontype.php');
    require_once('objectlayer/namevalue.php');
    
    $doubtquestionids_array = array();
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('savefordoubt', '=', '1'));
    $doubtquestions = new studentattemptedcollection($filter);
    // if there are no doubt questions, simply return an empty array
    if (sizeof($doubtquestions->getobjectcollection()) == 0){
      echo json_encode(array());

    } else {
      $retval = array();
      foreach($doubtquestions->getobjectcollection() as $doubtquestion){
        array_push($doubtquestionids_array, $doubtquestion->question_id);
      }
      $filter = array();
      array_push($filter, new NameValue('id', 'in', $doubtquestionids_array));
      array_push($filter, new NameValue('topic_id', 'in', $topicid_array));
      $questions = new questioncollection($filter);
      foreach($questions->getobjectcollection() as $question){        
        $question->questiontype = new questiontype($question->q_type_id);
        $choices = new choicecollection(new NameValue('question_id', '=', $question->id));
        $question->choices = $choices->getobjectcollection();
        $answer = new answercollection(new NameValue('question_id', '=', $question->id));
        $question->answer = $answer->getobjectcollection()[0];  // since there'll always be one and only one answer
        array_push($retval, $question);
      }
        echo json_encode($retval);
    }
  }

  function __obsolete_getnotesbytopics($student_id, $topicid_list){
    $topicid_array = explode(",",$topicid_list);
    require_once('objectlayer/questioncollection.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/questiontype.php');
    require_once('objectlayer/namevalue.php');
    
    $notequestionids_array = array();
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('isnote', '=', '1'));
    $notequestions = new studentattemptedcollection($filter);
    // if there are no note questions, simply return an empty array
    if (sizeof($notequestions->getobjectcollection()) == 0){
      echo json_encode(array());

    } else {
      $retval = array();
      foreach($notequestions->getobjectcollection() as $notequestion){
        array_push($notequestionids_array, $notequestion->question_id);
      }
      $filter = array();
      array_push($filter, new NameValue('id', 'in', $notequestionids_array));
      array_push($filter, new NameValue('topic_id', 'in', $topicid_array));
      $questions = new questioncollection($filter);
      foreach($questions->getobjectcollection() as $question){        
        $question->questiontype = new questiontype($question->q_type_id);
        $choices = new choicecollection(new NameValue('question_id', '=', $question->id));
        $question->choices = $choices->getobjectcollection();
        $answer = new answercollection(new NameValue('question_id', '=', $question->id));
        $question->answer = $answer->getobjectcollection()[0];  // since there'll always be one and only one answer
        array_push($retval, $question);
      }
        echo json_encode($retval);
    }
  }

  // when a student attempts a test, we send the whole activityObject.Subjects object with all selected choice.attempt
  function savetestquestionsattempted($student_id){
    require_once('objectlayer/studentattempted.php');
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
      $json = file_get_contents('php://input');
      $data = json_decode($json);
      $retval = array();
      foreach($data as $subject){
        foreach($subject->questions as $question){
          
          if (isset($question->attempt) && $question->attempt){
            $studentattempted = new studentattempted();
            $studentattempted->student_id = $student_id;
            $studentattempted->question_id = $question->id;
            if ($question->questiontype->name == 'mcq' || $question->questiontype->name == 'mmcq'){
              $total_correct_answers = 0;
              $correct_attempts = 0;
              foreach($question->choices as $choice){
                if ($choice->correct_ans == "1"){
                  $total_correct_answers += 1;
                }
                if (isset($choice->selected) && $choice->selected == true){
                  $correct_attempts += 1;
                }
              }
              $studentattempted->score = $correct_attempts/$total_correct_answers;
            } else if ($question->questiontype->name == 'fitb'){
              if ($question->choices[0]->description == $question.choices[0].fitb){
                $studentattempted->score = 1;
              } else {
                $studentattempted->score = 0;
              }
              
            }
            
            $studentattempted->attempts = 1;
            $studentattempted->savefordoubt = 0;
            $studentattempted->isnote = 0;
            $studentattempted->Save();
            array_push($retval,$studentattempted);
          }
          // IMPORTANT
          // we have no way to check if a Long answer question has been answered
          // so we go with the assumption if the question was viewed, it was answered
          if ($question->questiontype->name == 'long' && $question->viewed){
            $studentattempted = new studentattempted();
            $studentattempted->student_id = $student_id;
            $studentattempted->question_id = $question->id;
            $studentattempted->score = 0;
            $studentattempted->attempts = 1;
            $studentattempted->savefordoubt = 0;
            $studentattempted->isnote = 0;
            $studentattempted->Save();
            array_push($retval,$studentattempted);
          }

        }
      }
    }
    echo json_encode($retval);
  }


  function savestudentattempt($student_id,$question_id,$score,$attempts){
    require_once('objectlayer/studentattempted.php');
    $studentattempted = new studentattempted();
    $studentattempted->student_id = $student_id;
    $studentattempted->question_id = $question_id;
    $studentattempted->score = $score;
    $studentattempted->attempts = $attempts;
    $studentattempted->savefordoubt = 0;
    $studentattempted->isnote = 0;
    $studentattempted->Save();
    echo json_encode(__questions_attempted_today($student_id));
  }

  function savefordoubt($student_id,$question_id,$doubt_type){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/studentattempted.php');
    require_once('objectlayer/namevalue.php');
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('question_id', '=', $question_id));
    $studentattempteds = new studentattemptedcollection($filter);
    // we can also hit this case in a test, student can save for doubt, even if they haven't attempted the question
    $studentattempted = $studentattempteds->length == 1 ? $studentattempteds->getobjectcollection()[0] : new studentattempted();
    $studentattempted->question_id = $question_id;
    $studentattempted->student_id = $student_id;
    $studentattempted->student_id = $student_id;
    if ($studentattempted->savefordoubt != "1"){
      $studentattempted->savefordoubt = "1";
    } else {
      $studentattempted->savefordoubt = "0";
    }
    $studentattempted->doubttype = $doubt_type;
    $studentattempted->Save();
    echo json_encode($studentattempted);
  }

  function questionsattemptedtoday($student_id){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('timeattempted_ts', '>=', 'CURDATE()'));
    array_push($filter, new NameValue('timeattempted_ts', '<', 'CURDATE() + INTERVAL 1 DAY'));
    $studentattempteds = new studentattemptedcollection($filter);
    echo json_encode(__questions_attempted_today($student_id));
  }

  function __questions_attempted_today($student_id){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('timeattempted_ts', '>=', 'CURDATE()'));
    array_push($filter, new NameValue('timeattempted_ts', '<', 'CURDATE() + INTERVAL 1 DAY'));
    $studentattempteds = new studentattemptedcollection($filter);
    return $studentattempteds->getobjectcollection();
  }



  function saveasnote($student_id,$question_id){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('question_id', '=', $question_id));
    $studentattempteds = new studentattemptedcollection($filter);
    $studentattempted = $studentattempteds->getobjectcollection()[0];
    $studentattempted->isnote = "1";
    $studentattempted->Save();
    echo json_encode($studentattempted);
  }  


  function savedoubtcleared($student_id,$question_id){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('question_id', '=', $question_id));
    $studentattempteds = new studentattemptedcollection($filter);
    $studentattempted = $studentattempteds->getobjectcollection()[0];
    $studentattempted->savefordoubt = "2";
    $studentattempted->Save();
    echo json_encode($studentattempted);
  }

  function obsolete_updateanswerurl($answer_id,$answer_url){
    require_once('objectlayer/answer.php');
    $answer = new answer($answer_id);
    $answer->url = $answer_url;
    $answer->Save();
    echo json_encode(array("updatedURLID"=>$answer->id));
  }

  function __get_question_file_dir_locaton(){
    $c = 0;
    $question_files_dir = NULL;
    while (true){
      $question_files_dir = getcwd()."/question.files";
      if (file_exists($question_files_dir)){
        return $question_files_dir;
      }
      $c += 1;
      if ($c == 10){
        break;
      }
      chdir("..");
    }
    return "NOT FOUND";
  }


  function deletequestion($question_id){
    require_once('objectlayer/question.php');
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    require_once('objectlayer/answercollection.php');
    require_once('objectlayer/choicecollection.php');
    $retval = array("success"=>0,"err"=>"");
    $studentattempteds = new studentattemptedcollection(new NameValue('question_id', '=', $question_id));
    if (count($studentattempteds->getobjectcollection()) > 0){
      $retval['success'] = -1;
      $retval['err'] = "You cannot delete question that has already been attempted";
    } else {
      $question_files_dir = __get_question_file_dir_locaton();
      $answers = new answercollection(new NameValue('question_id', '=', $question_id));
      foreach($answers->getobjectcollection() as $answer){
        unlink($question_files_dir . '/' . $answer->file_name);
        $answer->Delete();
      }
      $choices = new choicecollection(new NameValue('question_id', '=', $question_id));
      foreach($choices->getobjectcollection() as $choice){
        unlink($question_files_dir . '/' . $choice->file_name);
        $choice->Delete();
      }
      $question = new question($question_id);
      unlink($question_files_dir . '/' . $question->file_name);
      $question->Delete();
      $retval['success'] = 1;
    }
    echo json_encode($retval);
  }

  function obsolete_savefordoubtcleared($student_id,$question_id){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('question_id', '=', $question_id));
    $studentattempteds = new studentattemptedcollection($filter);
    $studentattempted = $studentattempteds->getobjectcollection()[0];
    $studentattempted->savefordoubt = "";
    $studentattempted->Save();
    echo json_encode($studentattempted);
  }

  function obsolete_getstudentdoubtquestionids($student_id){
    require_once('objectlayer/studentattemptedcollection.php');
    require_once('objectlayer/namevalue.php');
    require_once('objectlayer/questioncollection.php');

    $filter = array();
    array_push($filter, new NameValue('student_id', '=', $student_id));
    array_push($filter, new NameValue('savefordoubt', '=', '1'));
    $studentdoubts = new studentattemptedcollection($filter);
    $doubt_question_ids = array();
    foreach($studentdoubts->getobjectcollection() as $studentdoubt) {
      array_push($doubt_question_ids, $studentdoubt->id);
    }
    $doubt_questions = new questioncollection(new NameValue('id', 'in', $doubt_question_ids));
    $retval = array();
    foreach($doubt_questions->getobjectcollection() as $doubt_question){
      array_push($retval,$doubt_question->id);
    }
    
    echo json_encode($retval);
  }
  

  function gettestlist(){
    require_once('objectlayer/testcollection.php');
    $tests = new testcollection();
    $jee = array();
    $cbse = array();
    foreach($tests->getobjectcollection() as $test) {
      if ($test->test_name == 'jee'){
        array_push($jee,$test);
      }
      else if ($test->test_name == 'cbse'){
        array_push($cbse,$test);
      }
    }
    echo json_encode(array('jee'=>$jee,'cbse'=>$cbse));
  }

  function gettestinfo($test_id){
    require_once('objectlayer/testtopiccollection.php');
    require_once('objectlayer/subject.php');
    require_once('objectlayer/topic.php');
    require_once('objectlayer/test.php');
    require_once('objectlayer/namevalue.php');
    $test = new test($test_id);
    $testtopics = new testtopiccollection(new NameValue('test_id', '=', $test_id));
    foreach($testtopics->getobjectcollection() as $testtopic){
      $topic = new topic($testtopic->topic_id);
      $subject = new subject($topic->subject_id);

    }

    echo json_encode($test);

  }

  // Credit: https://www.w3schools.com/php/func_mail_mail.asp
  function telladminnoquestionsleft($student_id){
    require_once('objectlayer/appuser.php');
    $user = new appuser($student_id);
    // the message
    $message = "Dear Mr. Admin,\nI have no questions left to do.\n" . $user->firstname . ' ' . $user->lastname;
    
    // use wordwrap() if lines are longer than 70 characters
    $message = wordwrap($message,70);
    // send email
    $headers = 'From: contactus@peterb.in' . "\r\n" . 'Reply-To: webmaster@example.com' . "\r\n" . 'X-Mailer: PHP/' . phpversion();
    mail("gapeterb@gmail.com","No questions left",$message,$headers);
    echo json_encode($user);
  }

?>
