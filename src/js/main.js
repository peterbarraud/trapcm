// credit: [davidguttman](https://gist.github.com/davidguttman/1f61ab59349cb99d28a1)
// include js

const { Modal } = require('bootstrap');

class InfoModal extends Modal {
  constructor(title, body){
    $('#info-modal-title').text(title);
    $('#info-modal-body').html(body);
    super($('#info-modal'));
  }
}

// Bootstrap wants jQuery global
window.jQuery = $  = require('jquery');
// For some reason, I get a Tether not found error (but sometimes). If you do get this error, uncomment the next line
// window.Tether = require('tether');
window.Popper = require('popper.js');
require('bootstrap');
const activityObject = {
  Questions : null,
  CurrentSubject : null,
  ActivityType : null,
  ActivityTitle : null,
  Test: {},
  Config: null,
  AttemptedQuestion:null,
  AttemptedQuestionIndex:1
};

const Direction = Object.freeze({ 
  NONE: 0,
  PREVIOUS: -1,
  NEXT: 1,
  BYINDEX:2
});

const ACTIVITYTYPE = Object.freeze({ 
  QUESTIONAIRE: 1,
  TEST: 2,
  DOUBTS: 3, 
  NOTES: 4,
  TESTRESULT:5,
  NONE:6
});


var studentObject = {};
var topicList = [];


function addAnswerDetails(question){
  let answer = question.answer;
  if (question.is_jee_advanced === '1'){
    $('#jee-advanced-display').html(' (JEE Advanced question)');
  } else {
    $('#jee-advanced-display').html('');
  }
  if (answer.description){
    $("#answer-description").html(answer.description);
  } else {
    $("#answer-screenshot").attr("src", answer.imgsrc);
  }
  if (answer.url){
    $("#answer-url").show().attr("href",answer.url).text("Learn more");
    $("#no-answer-url").hide()
  } else {
    $("#answer-url").hide();
    $("#no-answer-url").show();
  }
}

function submitAnswer(){
  var question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];
  question.Attempts += 1;
  // allowChangingTabs(question);
  var gotCorrectAnswerIDList = [];
  // in an mcq, disable other subject tabs as long as question is completely answered
  if(question.questiontype.name == 'mcq' || question.questiontype.name == 'mmcq'){ 
    if (question.Attempts === 1){
      $('#the-questionaire ul li button').each(function(){
        $(this).addClass('disabled');
      });
      // first attempt so only iterate over the options the student has picked
      $("input[name*='choice']:checked").each(function(){
        if (question.correctAnsIDList.includes(this.id)){
          $(this).parent().addClass("correct-answer");
          gotCorrectAnswerIDList.push(this.id);
          $('#the-questionaire ul li button').each(function(){
            $(this).removeClass('disabled');
          });
        } else {
          $(this).parent().addClass("incorrect-answer");
          $('#attempt-answer').text("Try again");
        }
      });
      
  
    }
    if (question.Attempts === 2 || gotCorrectAnswerIDList.length === question.correctAnsIDList.length){
      $('#the-questionaire ul li button').each(function(){
        var score = gotCorrectAnswerIDList.length/question.correctAnsIDList.length;
        __question_attempts_over(score,question);
    
      });  
      $("input[name*='choice']").each(function(){
        if (question.correctAnsIDList.includes(this.id)){
          $(this).parent().addClass("correct-answer");
          if ($(this).is(":checked")){
            gotCorrectAnswerIDList.push(this.id);
          }
        } else {
          if ($(this).is(":checked")){
            $(this).parent().addClass("incorrect-answer");
          }
        }
        
      });
    }
  
  } else if (question.questiontype.name == 'long'){
    __question_attempts_over(1,question);
  } else if (question.questiontype.name == 'fitb'){
    if ($('[name=fitb]').val().trim() === question.choices[0].description.trim()){
      $('[name=fitb]').addClass('correct-answer');
      __question_attempts_over(1,question);
    } else {
      if (question.Attempts === 1){
        $('#the-questionaire ul li button').each(function(){
          $(this).addClass('disabled');
        });
        $('[name=fitb]').addClass('incorrect-answer');
        $('#attempt-answer').text("Try again");
      } else {
        $('[name=fitb]').val("Your answer: " + $('[name=fitb]').val() + "; Correct answer is: " + question.choices[0].description.trim());
        __question_attempts_over(0,question);
      }

    }
  }
}

function __question_attempts_over(score,question){
  $("#pause-question").hide();
  question.score = score;
  question.times.push(Date.now());
  if (question.times.length/2 != Math.floor(question.times.length/2)){
    print("gotcha");
  }
  let timeTaken = 0;
  $(question.times).each(function(idx, quesitonTime){
    if (idx/2 == Math.floor(idx/2)){
      timeTaken += question.times[idx+1] - question.times[idx];
    }
  });
  question.timeTaken = Math.round((timeTaken)/1000);
  
  $('#the-questionaire ul li button').each(function(){
    $(this).removeClass('disabled');
  });

  $('[name=navigate-question][direction="1"]').prop('disabled', activityObject.CurrentSubject.CurrentQuestionIndex + 1 === activityObject.CurrentSubject.questions.length);
  $("#attempt-answer").hide();
  __setNavigationButtonState();
  $('[name=navigate-question][direction="1"],[name=answer-details-button],[name=manage-doubts], [name=manage-notes]').show();
  $('[name=manage-doubts]').text("Save for doubt").removeClass('disabled');
  $("[name=manage-notes]").text("Save as note");

  const ajaxUrl = activityObject.Config.rest_api_base_url + "savestudentattempt/" + studentObject.id;
  $.post(ajaxUrl, JSON.stringify(question), function(result){
    __setTodaysQuestions(result);
  }); 

}

function storeStudentAttempt(){
  var question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];
  if (question.questiontype.name == 'mcq' || question.questiontype.name == 'mmcq'){
    $("input[name=choice]:checked").each(function(){
      let checkbox = this;
      question.choices.map(function(choice){
        if (choice.id === $(checkbox).attr('choice-id')){
          choice.selected = true;
        }
      });  
      question.attempt = true;
    });
  } else if (question.questiontype.name == 'fitb'){
    question.choices[0].fitb = $('[name=fitb]').val();
    question.attempt = true;
  }
  
}

function __setupQuestionNumberList(){
  $('#question-number-list').empty();
  activityObject.CurrentSubject.questions.map(function(question, index){
    let buttonClass = "btn btn-light";
    let buttonText = index + 1;
    if (question.viewed){
      buttonClass = "btn btn-warning";
    }
    if (question.attempt){
      buttonClass = "btn btn-success";
    }
    if (question.bookmark){
      buttonText += '<sup>&#128204;</sup>';
    }




    if (index === activityObject.CurrentSubject.CurrentQuestionIndex){
      buttonClass += " disabled";
    }
    buttonClass += ' outline-button'
    $('<button>', {
      html : buttonText,
      class: buttonClass,
      style:"margin:1px",
      "question-index":index,
      name:"number-list-item"
    }).appendTo($('#question-number-list'));

  });  
}

function setupTestQuestion(direction=Direction.NEXT, questionIndex){
  $("[name=manage-doubts]").text("Save for doubt");
  $("[name=manage-notes]").text("Save as note");
  if (direction == Direction.BYINDEX){
    activityObject.CurrentSubject.CurrentQuestionIndex = questionIndex;
  } else {
    activityObject.CurrentSubject.CurrentQuestionIndex += direction;
  }

  

  // there is no "else". Why? I'm glad you asked
  // Because if the user got here without direction, means stays put
  // new question comes up so right now no attempts have been made
  var question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];

  // as soon as we get here, the question is viewed
  question.viewed = true;

  addAnswerDetails(question);

  __setNavigationButtonState();

  // set bookmark state
  if (question.bookmark){
    $('[name=bookmark-question').removeClass('btn-outline-primary').addClass('btn-primary').attr('title',"Remove question bookmark");
  } else {
    $('[name=bookmark-question').removeClass('btn-primary').addClass('btn-outline-primary').attr('title',"Bookmark this question");
  }
  

  // clean up the previous question
  // remove all choices
  $('#test-choices').empty();
  $('#the-test-question').empty();
  // now set up the question markup
  let fileStrPrefix = 'data:image/png;base64, '
  question.imgsrc = question.filestr ? fileStrPrefix + question.filestr : 'question.files/' + question.file_name;
  question.choices.map(function(choice){
    choice.imgsrc = choice.filestr ? fileStrPrefix + choice.filestr : 'question.files/' + choice.file_name;
  });
  question.answer.imgsrc = question.answer.filestr ? fileStrPrefix + question.answer.filestr : 'question.files/' + question.answer.file_name;

  // if already attempted, then don't reset
  if (question.hasOwnProperty('Attempts') == false){
    question.Attempts = 0;
  }
  
  $('<p>', {
    html : `<span class='questiontypedesc'>${__getQuestionTypeDescription(question.questiontype.name)}</span>`
  }).appendTo($('#the-test-question'));  

  // the quesiton gets put for all question types
  if (question.description){
    $('<p>', {
      html : question.description
    }).appendTo($('#the-test-question'));

  } else {
    $('<img>', {
      src : question.imgsrc
    }).appendTo($('#the-test-question'));  
  }
  // for tests, we will indicate clearly mcq vs mmcq
  question.choices.map(function(choice){
    if (question.questiontype.name === 'mcq' || question.questiontype.name === 'mmcq'){
      let questionType = question.questiontype.name == 'mcq' ? "radio" : "checkbox";
      var listItem = document.createElement('li');
      $(listItem).addClass('list-group-item');
      var choiceHolder = document.createElement('div');
      $(choiceHolder).addClass('choice-holder');
      $('<input>', {
        type: questionType,
        name:"choice",
        "choice-id":choice.id,
        checked:choice.selected,
        "read-only":true
      }).appendTo(choiceHolder);
    if (choice.description){
        $('<span>', {
          html : choice.description,
          style: "margin-left:5px"
        }).appendTo($(choiceHolder));

      } else {
        $('<img>', {
          src : choice.imgsrc
        }).appendTo($(choiceHolder));  
      }
      if (activityObject.ActivityType === ACTIVITYTYPE.TESTRESULT){
        if (choice.correct_ans === "1"){
          $(choiceHolder).addClass("correct-answer");
        }
        if (choice.selected && choice.correct_ans === "0"){
          $(choiceHolder).addClass("incorrect-answer");
        }
      }
      $(listItem).append(choiceHolder);
      $('#test-choices').append(listItem);
    } else if (question.questiontype.name === 'fitb'){
      $('<input>', {
        type:"text",
        name:"fitb",
        placeholder:"Enter your answer here",
        style:"margin-bottom:4px",
        value:question.choices[0].fitb
      }).appendTo('#test-choices');
      if (activityObject.ActivityType === ACTIVITYTYPE.TESTRESULT){
        if (question.choices[0].fitb.trim() === question.choices[0].description.trim()){
          $('[name=fitb]').addClass("correct-answer");
        } else {
          $('[name=fitb]').addClass("incorrect-answer");
          $('<div>', {
            class:"alert alert-danger",
            role:"alert",
            id:'incorrect-answer-alert',
            text:"Correct answer is: " + question.choices[0].description.trim()
          }).insertAfter($('[name=fitb]'));
          // $('[name=fitb]').val("Your answer: " + question.choices[0].fitb + "; Correct answer is: " + question.choices[0].description.trim());  
        }
      }
  
    }
  });
  __setupQuestionNumberList();
} 


function setupDoubtOrNoteQuestion(questionIncrement=0){
  activityObject.CurrentSubject.CurrentQuestionIndex  += questionIncrement;
  var question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];

  // set up the questions button menu
  $('[name=answer-details-button],[name=manage-doubts], [name=manage-notes]').show();
  $("#attempt-answer").hide();
  $("[name=manage-notes]").text("Save as note");
  $('[name=navigate-question][direction="1"][name=navigate-question][direction="-1"]').show();
  __setNavigationButtonState();
  if (question.savefordoubt === '1'){
    $('[name=manage-doubts]').removeClass('disabled').text('Mark as doubt cleared');
  } else if (question.savefordoubt === '2'){
    $('[name=manage-doubts]').addClass('disabled').text('Doubt cleared');
  }

  // clean up the previous question
  // remove all choices
  $('#question-choices').empty();
  $('#the-question').empty();

  
  // either by clicking next from the previous question. In which case, they should see the options to answer the question
  // else, by answering this question and then going away to answer another from another subject WITHOUT first clicking Next
  // let's try to handle this

  // we are now going to accomodate text (description) for question and choices
  // SUPER IMPORTANT CODE CHANGE
  // Since we are moving from files to filestring, the following code changes are required
  // however, for backward compatibility, we will continue to support files
  // so, if filestr is empty then use file
  let fileStrPrefix = 'data:image/png;base64, '
  question.imgsrc = question.filestr ? fileStrPrefix + question.filestr : 'question.files/' + question.file_name;
  question.choices.map(function(choice){
    choice.imgsrc = choice.filestr ? fileStrPrefix + choice.filestr : 'question.files/' + choice.file_name;
  });
  question.answer.imgsrc = question.answer.filestr ? fileStrPrefix + question.answer.filestr : 'question.files/' + question.answer.file_name;


  addAnswerDetails(question);

  // for doubt questions, we are showing the Question ID
  // and the doubt-type
  let doubtType = '';
  if (question.doubttype === 'ba'){
    doubtType = "Incorrect answer ";
  } else if (question.doubttype === 'da'){
    doubtType = "Different answer ";
  }
  let doubtDescription = '';
  if (question.doubtdescription){
    doubtDescription = `<b>Doubt details</b>: ${question.doubtdescription}`;
  }
  $('<span>', {
    html : `QuestionID: <b>${question.id}</b>: <i>${doubtType}</i> ${doubtDescription}`
  }).appendTo($('#the-question'));

  // the quesiton gets put for all question types
  if (question.description){
    $('<p>', {
      html : question.description
    }).appendTo($('#the-question'));

  } else {
    $('<img>', {
      src : question.imgsrc
    }).appendTo($('#the-question'));  
  }
  if (question.questiontype.name == 'mcq' || question.questiontype.name == 'mmcq'){
      question.correctAnsIDList = [];
      question.choices.map(function(choice){
        if (choice.correct_ans === "1"){
          question.correctAnsIDList.push(choice.id);
        }
      });
    }
  question.choices.map(function(choice){
    var listItem = document.createElement('li');
    $(listItem).addClass('list-group-item');
    var choiceHolder = document.createElement('div');
    $(choiceHolder).addClass('choice-holder');
    if (choice.description){
      $('<span>', {
        html : choice.description,
        style: "margin-left:5px"
      }).appendTo($(choiceHolder));

    } else {
      $('<img>', {
        src : choice.imgsrc
      }).appendTo($(choiceHolder));  
    }
    $(listItem).append(choiceHolder);
    if (choice.correct_ans === "1"){
      $(choiceHolder).addClass("correct-answer");
    }

    $('#question-choices').append(listItem);
  });
}


function __setNavigationButtonState(){
  if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE){
    $('[name=navigate-question][direction="-1"]').hide();
  } if (activityObject.ActivityType === ACTIVITYTYPE.DOUBTS){
    $('[name=navigate-question][direction="-1"]').show();
  } 
  // disable next if we are at the end
  $('[name=navigate-question][direction="1"]').prop('disabled', activityObject.CurrentSubject.CurrentQuestionIndex + 1 === activityObject.CurrentSubject.questions.length);

  // disable previous if we are at the start
  $('[name=navigate-question][direction="-1"]').prop('disabled', activityObject.CurrentSubject.CurrentQuestionIndex === 0);
}

// Since the db could get very large, at one questionaire at a time, we don't want to get too many questions
// so, as we navigate through the questionaire, we are going to check if we're getting to the end of the last got questions
// if we are (and before we actually reach the end), we will get more questions
// which means as long as there are questions in the DB and as long as the student keeps progress, the questionaire will never end!
function __getMoreQuestions(){
  let questionsDone = activityObject.CurrentSubject.CurrentQuestionIndex + 1;
  let quesitons = activityObject.CurrentSubject.questions;
  if (quesitons.length - questionsDone <= 2){
    let topics = [];
    let questionIDs = [];
    $(activityObject.CurrentSubject.questions).each(function(){
      questionIDs.push(this.id);
    });
    $(quesitons).each(function(){
      if (!topics.includes(this.topic_id)){
        topics.push(this.topic_id);
      }
    });
  
    var ajaxUrl = `${activityObject.Config.rest_api_base_url}getquestions/${studentObject.id}/${topics.toString()}`;
    $.ajax({url: ajaxUrl, success: function(result){
      let subjects = JSON.parse(result);
      if (subjects.length){
        $(subjects[0].questions).each(function(){
          if (!questionIDs.includes(this.id)){
            activityObject.CurrentSubject.questions.push(this);
          }
        });
      }
    }});
    


  }
}

function __getQuestionTypeDescription(quesitonTypeName){
  let questionTypeDescription = '';
  if (quesitonTypeName == 'mcq'){
    questionTypeDescription = 'Only one correct option';
  } else if (quesitonTypeName == 'mmcq'){
    questionTypeDescription = 'One or more than one correct options';
  } else if (quesitonTypeName == 'fitb'){
    questionTypeDescription = 'Fill-in-the-blanks';
  } else if (quesitonTypeName == 'long'){
    questionTypeDescription = 'Long answer type';
  }
  return questionTypeDescription;
}

// called when student opens the attempted questions modal.
// this is just a lookback of what's been done
function setupAttemptedQuestion(){
  var ajaxUrl = activityObject.Config.rest_api_base_url + "getattemptedquestion/" + activityObject.AttemptedQuestionIndex;
  $.ajax({url: ajaxUrl, success: function(result){
    try {
      activityObject.AttemptedQuestion = JSON.parse(result);
      if (activityObject.AttemptedQuestion.doubttype === ''){
        activityObject.AttemptedQuestion.doubttype = null;
      }
      $("#attempted-questions-err").addClass("invisible");
      $('#attempted-question-type, #attempted-answer, #attempted-question').empty()
      $("[name=navigate-attempted-question][direction=1]").prop("disabled",false);
      $('<p>', {
        html : `<span class='questiontypedesc'>${__getQuestionTypeDescription(activityObject.AttemptedQuestion.questiontype.name)}</span>`
      }).appendTo($('#attempted-question-type'));
      if (activityObject.AttemptedQuestion.answer.url){
        $('<a>', {
          href : activityObject.AttemptedQuestion.answer.url,
          target:"_blank",
          text: "Learn more"
        }).appendTo($('#attempted-question-type'));  
      } else {
        $('<p>', {
          text: "No Learn more link available"
        }).appendTo($('#attempted-question-type'));  

      }
      let fileStrPrefix = 'data:image/png;base64, '
      if (activityObject.AttemptedQuestion.description){
        $('<p>', {
          html : activityObject.AttemptedQuestion.description
        }).appendTo($('#attempted-question'));
      } else {
        $('<img>', {
          src : activityObject.AttemptedQuestion.filestr ? fileStrPrefix + activityObject.AttemptedQuestion.filestr : 'question.files/' + activityObject.AttemptedQuestion.file_name
        }).appendTo($('#attempted-question'));  
      }
      let listGroup = null;
      if (activityObject.AttemptedQuestion.choices){
        listGroup = document.createElement('ul');
        $(listGroup).addClass('list-group').appendTo($('#attempted-question'));

      }
      activityObject.AttemptedQuestion.choices.map(function(choice){
        listItem = document.createElement('li');
        $(listItem).addClass('list-group-item').appendTo(listGroup);
        if (choice.description){
          $('<span>', {
            html : choice.description,
            style: "margin-left:5px"
          }).appendTo($(listItem));
  
        } else {
          $('<img>', {
            src : choice.filestr ? fileStrPrefix + choice.filestr : 'question.files/' + choice.file_name
          }).appendTo($(listItem));  
        }
        if (choice.correct_ans === "1"){
          $(listItem).addClass("list-group-item-success");
        }
    
      });      

      if (activityObject.AttemptedQuestion.answer.description){
        $('<p>', {
          html : activityObject.AttemptedQuestion.answer.description
        }).appendTo($('#attempted-answer'));
      } else {
        $('<img>', {
          src : activityObject.AttemptedQuestion.answer.filestr ? fileStrPrefix + activityObject.AttemptedQuestion.answer.filestr : 'question.files/' + activityObject.AttemptedQuestion.answer.file_name
        }).appendTo($('#attempted-answer'));
      }
    } catch (err){
      console.log(err);
      $("#attempted-questions-err").removeClass("invisible");
      $("[name=navigate-attempted-question][direction=1]").prop("disabled",true);
    }

  }});

}

// this is a questionarie question
function setupQuestion(questionIncrement=0){
  
  __getMoreQuestions();
  activityObject.CurrentSubject.CurrentQuestionIndex  += questionIncrement;
  // new question comes up so right now no attempts have been made
  var question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];
  question.times = [];
  question.times.push(Date.now());
  // in a questionaire, this is definitely the first time we're hitting this question so
  question.doubttype = null;

  // clean up the previous question
  // remove all choices
  $('#question-choices').empty();
  $('#the-question').empty();

  if (question.questiontype.name === 'long'){
    question.Attempts = 1;
    __question_attempts_over(1,question);    
} else {
    if (question.Attempts > 1 || (question.Attempts > 0 && question.questiontype.name === 'fitb')){ // this can only come from subject tab toggle
      // and question has already been attempted
      $("#attempt-answer").hide();
      __setNavigationButtonState();
      $('[name=answer-details-button],[name=manage-doubts], [name=manage-notes]').show();
    } else {
      $("#attempt-answer").show().text("Submit answer");
      $('[name=navigate-question],[name=answer-details-button],[name=manage-doubts], [name=manage-notes]').hide();
    }
      
  }

  // at this point, we (hopefully) have enough info to decide the question button menu


  // we are now going to accomodate text (description) for question and choices
  // SUPER IMPORTANT CODE CHANGE
  // Since we are moving from files to filestring, the following code changes are required
  // however, for backward compatibility, we will continue to support files
  // so, if filestr is empty then use file
  let fileStrPrefix = 'data:image/png;base64, '
  question.imgsrc = question.filestr ? fileStrPrefix + question.filestr : 'question.files/' + question.file_name;
  question.choices.map(function(choice){
    choice.imgsrc = choice.filestr ? fileStrPrefix + choice.filestr : 'question.files/' + choice.file_name;
  });
  question.answer.imgsrc = question.answer.filestr ? fileStrPrefix + question.answer.filestr : 'question.files/' + question.answer.file_name;

  // if already attempted, then don't reset
  if (question.hasOwnProperty('Attempts') == false){
    question.Attempts = 0;
  }
  addAnswerDetails(question);
  // let pauseButton = '<span class="pause-question">&#x23F8;</span>';<button type="button" class="btn btn-secondary btn-sm">Small button</button>
  let pauseButton = '<button type="button" class="btn btn-primary btn-sm pause-question" title="Pause question" id="pause-question">&#9612;&#9612;</button>';
  // let pauseButton = '<button type="button" class="btn btn-primary btn-xs">&#x23F8;</button>';
  $('<p>', {
    html : `<span class='questiontypedesc'>${__getQuestionTypeDescription(question.questiontype.name)}</span>&nbsp;${pauseButton}`
  }).appendTo($('#the-question'));  
  // the quesiton gets put for all question types
  if (question.description){
    $('<p>', {
      html : question.description
    }).appendTo($('#the-question'));

  } else {
    $('<img>', {
      src : question.imgsrc
    }).appendTo($('#the-question'));  
  }

  if (question.questiontype.name == 'mcq' || question.questiontype.name == 'mmcq' || question.questiontype.name == 'fitb'){
      question.correctAnsIDList = [];
      question.choices.map(function(choice){
        if (choice.correct_ans === "1"){
          question.correctAnsIDList.push(choice.id);
        }
      });
    }
  question.choices.map(function(choice){
    if (question.questiontype.name == 'mcq' || question.questiontype.name == 'mmcq'){
      let questionType = question.questiontype.name == 'mcq' ? "radio" : "checkbox";
      var listItem = document.createElement('li');
      $(listItem).addClass('list-group-item');
      var choiceHolder = document.createElement('div');
      $(choiceHolder).addClass('choice-holder');
      $('<input>', {
        type:questionType,
        name:"choice",
        id:choice.id
      }).appendTo(choiceHolder);
      if (choice.description){
        $('<span>', {
          html : choice.description,
          style: "margin-left:5px"
        }).appendTo($(choiceHolder));

      } else {
        $('<img>', {
          src : choice.imgsrc
        }).appendTo($(choiceHolder));  
      }
      $(listItem).append(choiceHolder);
      $('#question-choices').append(listItem);
    } else if (question.questiontype.name == 'fitb'){
      $('<input>', {
        type:"text",
        name:"fitb",
        placeholder:"Enter your answer here",
        style:"margin-bottom:4px"
      }).appendTo('#question-choices');
    }

  });
}


// start a questionaire - for questions, doubts, or notes
function startActivity(){
  activityObject.CurrentQuestionIndex = -1;
  var topics = Array();
  $( "input[name*='topic']:checked").each(function(){
    topics.push(this.id);
  });
  if (topics.length){
    var ajaxUrl = activityObject.Config.rest_api_base_url;
    if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE){
      ajaxUrl += "getquestions/";
    } else if (activityObject.ActivityType === ACTIVITYTYPE.DOUBTS){
      ajaxUrl += "getdoubtquestions/";
    } else if (activityObject.ActivityType === ACTIVITYTYPE.NOTES){
      ajaxUrl += "getnotequestions/";
    }
    ajaxUrl += studentObject.id + "/" + topics.toString();
    $.ajax({url: ajaxUrl, success: function(result){
      let subjects = JSON.parse(result);
      if (subjects.length){
        activityObject.Subjects = {};
        // let's add a property to each subject for the currently question index
        let isDefaultTab = true;
        // clean up tabs first
        $('#the-questionaire ul').empty();
        subjects.forEach((subject) => {
          subject.CurrentQuestionIndex = 0;
          let tabClass = isDefaultTab ? "nav-link active" : "nav-link";
          // setup the subject tabs
          $('<li>', {
            class:"nav-item",
            role:"presentation",
            html:'<button class="'+ tabClass + '" data-bs-toggle="tab" data-bs-target="#question-container" type="button" role="tab" subject-name="' + subject.name + '">' + subject.title + '</button>'
          }).appendTo($('#the-questionaire ul'));
          isDefaultTab = false;
          activityObject.Subjects[subject.name] = subject;
        });
        // default to the first subject
        activityObject.CurrentSubject = subjects[0];
        // and check that the first topic has some questions
        if (activityObject.CurrentSubject.questions.length){
          $('#topic-chooser').hide();
          $('#the-questionaire').show();
          if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE){
            setupQuestion();
          } else {
            setupDoubtOrNoteQuestion();
          }
          
        } else {
          (new InfoModal("Start test",'<p class="lead">There seem to be no unanswered questions in this topic</p><hr class="my-4"><p>You\'ll need to talk to the Admin.</p>')).show();
        }
      } else {

        (new InfoModal("Start test",'<p class="lead">There seem to be no unanswered questions in this topic</p><hr class="my-4"><p>You\'ll need to talk to the Admin.</p>')).show();

      }
    }});
  
  } else {
    startTestErrorMsg("You need to select at least one topic to get started");
  }
}

function startTestErrorMsg(body=null){
  body = body ? body : "There seem to be no unanswered questions in this topic";
  (new InfoModal("Start test error", body)).show();
}

function __getTestTime(){
  if (activityObject.Test.TestName === "jee"){
    // JEE - 2.4 mins per question
    let numberOfQuestions = 0;
    activityObject.Test.subjects.forEach((subject) => {
      numberOfQuestions += subject.questions.length;
    });
    // rounding up the mins
    let timeInMins = Math.ceil(numberOfQuestions * 2.4);
    // return time in seconds
    return timeInMins * 60;
  
  }

}

function __getTestTimeDisplay(){
  let hours = Math.floor(activityObject.Test.TimeRemaining/3600);
  let balance = activityObject.Test.TimeRemaining - hours*3600;
  let mins = Math.floor(balance/60);
  let secs = activityObject.Test.TimeRemaining - mins*60;
  return `${hours.toString().padStart(2,"0")}:${mins.toString().padStart(2,"0")}:${secs.toString().padStart(2,"0")}`;
}

// this is called by setInterval
function testTimer() {
  activityObject.Test.TimeRemaining -= 1;
  // warning if time is only 5 mins left (300 seconds)
  // but only if the user hasn't initiated force submit
  if (!activityObject.Test.ForceSubmit){
    if (activityObject.Test.TimeRemaining === 300){
      (new InfoModal("Nearly over!",'<p class="lead">You only have 5 minutes left. Hurry up</p>')).show();
  
    }  
  }
  if (activityObject.Test.TimeRemaining === 0){
    (new InfoModal("Timeout!",'<p class="lead">You have run out of time. Close this dialog and review your answers</p>')).show();
    clearInterval(activityObject.Test.Timer);
    submitTest();
  }
  $("#test-timer").text(__getTestTimeDisplay());
}
// opens start test modal
// IMPORTANT
// we are getting all the info for the selected test before the Start test modal
// this is because we need test info for the start test modal
// stuff like how many questions there are and the time to do the test
// and we figured that the best way to get this info is from the test info
function testStarter(testID, testName, testTitle){
  activityObject.Test.ID = testID;
  activityObject.Test.TestName = testName;
  activityObject.Test.Title = testTitle;
  var ajaxUrl = activityObject.Config.rest_api_base_url + "gettestquestions/" + studentObject.id + "/" + activityObject.Test.ID;
  $.ajax({url: ajaxUrl, success: function(result){
    activityObject.Test.subjects = JSON.parse(result);
    if (activityObject.Test.subjects.length){
      // open the start test modal
      activityObject.ActivityType = ACTIVITYTYPE.TEST;
      var startTestModal = new Modal($('#start-test-modal'));
      activityObject.Test.StartTestModal = startTestModal;
      let modalInfoTable = $("#start-test-modal table");
      $(modalInfoTable).empty();
      let tr = document.createElement('tr');
      $(tr).appendTo(modalInfoTable);

      $('<td>', {
        text : "Test"
      }).appendTo($(tr));         
      $('<td>', {
        html : activityObject.Test.Title
      }).appendTo($(tr));         

      tr = document.createElement('tr');
      $(tr).appendTo(modalInfoTable);
      $('<td>', {
        text : "Type"
      }).appendTo($(tr));         
      $('<td>', {
        html : activityObject.Test.TestName
      }).appendTo($(tr)); 


      tr = document.createElement('tr');
      $(tr).appendTo(modalInfoTable);
      $('<td>', {
        text : "Time"
      }).appendTo($(tr)); 
      
      activityObject.Test.Time = activityObject.Test.TimeRemaining = __getTestTime();
      $('<td>', {
        html : __getTestTimeDisplay()
      }).appendTo($(tr)); 

      tr = document.createElement('tr');
      $(tr).appendTo(modalInfoTable);
      $('<td>', {
        text : "Subjects",
        colspan:2
      }).appendTo($(tr));         

      activityObject.Test.subjects.forEach((subject) => {
        let tr = document.createElement('tr');
        $(tr).appendTo(modalInfoTable);
        $('<td>', {
          html : subject.title
        }).appendTo($(tr));      
        $('<td>', {
          html : `${subject.questions.length} questions`
        }).appendTo($(tr));         

      });
      startTestModal.show();

    } else {
      startTestErrorMsg("There seem to be no questions left in this test");
    }
  }});

}

// click of Start button on start test modal (actually start the test)
function startTest(){
  $('#the-test').closest('main').removeClass('col-6').addClass('col-10');
  $("[name=back-to-activity-chooser]").hide();
  $('#submit-test').prop('disabled',false);
  $("#test-timer").text(__getTestTimeDisplay()).closest("div").show();
  
  activityObject.Subjects = {};
  // let's add a property to each subject for the currently question index
  let isDefaultTab = true;
  // clean up tabs first
  $('#the-test ul').empty();
  activityObject.Test.subjects.forEach((subject) => {
    subject.CurrentQuestionIndex = 0;
    let tabClass = isDefaultTab ? "nav-link active" : "nav-link";
    // setup the subject tabs
    $('<li>', {
      class:"nav-item",
      role:"presentation",
      html:'<button class="'+ tabClass + '" data-bs-toggle="pill" data-bs-target="#question-container" type="button" role="tab" subject-name="' + subject.name + '">' + subject.title + '</button>'
    }).appendTo($('#the-test ul'));
    isDefaultTab = false;
    activityObject.Subjects[subject.name] = subject;
  });
  // default to the first subject
  activityObject.CurrentSubject = activityObject.Test.subjects[0];
  // and check that the first topic has some questions
  if (activityObject.CurrentSubject.questions.length){
    $('#subjects-row').empty();
    $('#topics-row').empty();
    $('#activity-chooser').hide();
    $('#the-test').show();
    $("#start-activity").text(activityObject.ActivityTitle);
    $('#today-question-counter').hide();
    $('[name=answer-details-button],[name=manage-doubts], [name=manage-notes]').hide();
    // first let's do this:
    // if the student got here from a previous question and checked some answers (in MCQ or MMCQ)
    storeStudentAttempt();
    setupTestQuestion(Direction.NONE);
    activityObject.Test.StartTestModal.hide();
    activityObject.Test.Timer = setInterval(testTimer, 1000);
    activityObject.Test.EndModal = new Modal($('#test-end-modal'));
  } else {
    startTestErrorMsg();
  }  
}

function submitTest(forceSubmit=false){
  if (forceSubmit == false && activityObject.Test.TimeRemaining > 60){
    $('#time-left').text(__getTestTimeDisplay());
    activityObject.Test.ForceSubmit = true;
    activityObject.Test.EndModal.show();
    
  } else {
    clearInterval(activityObject.Test.Timer);
    $("[name=answer-details-button]").show();
    $('[name=manage-doubts]').show().text("Save for doubt");
    $("[name=manage-notes]").show().text("Save as note");
    storeStudentAttempt();
    var ajaxUrl = activityObject.Config.rest_api_base_url + "savetestquestionsattempted/" + studentObject.id;
    $.post(ajaxUrl, JSON.stringify(activityObject.Subjects), function(result){
      let retval = JSON.parse(result);
      activityObject.ActivityType = ACTIVITYTYPE.TESTRESULT;
      setupTestQuestion(Direction.NONE);
    }); 
    $("#submit-test").prop("disabled",true);
    $("[name=back-to-activity-chooser]").show();
  
  }
}

function load_subjects_and_topics(testName){
  var ajaxUrl = activityObject.Config.rest_api_base_url;
  topicList = [];
  if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE){
    ajaxUrl += 'getsubjectsandtopicsunanswered/' + studentObject.id + "/" + testName;
  } else if (activityObject.ActivityType == ACTIVITYTYPE.DOUBTS){
    ajaxUrl += 'getsubjectsandtopicsdoubts/' + studentObject.id;
  } else if (activityObject.ActivityType == ACTIVITYTYPE.NOTES){
    ajaxUrl += 'getsubjectsandtopicsnotes/' + studentObject.id;
  }
  $.ajax({url: ajaxUrl, success: function(result){
    var subjectsandtopics = JSON.parse(result);
    if (subjectsandtopics.length > 0){
      // clean up any previous stuff
      $('#subjects-row').empty();
      $('#topics-row').empty();
      $('#activity-chooser').hide();
      $('#topic-chooser').show();
      $("#start-activity").text(activityObject.ActivityTitle);

      subjectsandtopics.map(function(subject){
        var subject_div = document.createElement("div");
        $(subject_div).addClass('col');
        $('<button>', {
          type:"button",
          class:"btn btn-outline-primary",
          name:"all-topic-selector",
          "subject-id":subject.id,
          text:subject.title,
          "selected-all":0
        }).appendTo(subject_div);
        $('#subjects-row').append(subject_div);
      });
      subjectsandtopics.map(function(subject){
        var topic_div = document.createElement("div");
        $(topic_div).addClass('col');
        var ul = document.createElement("ul");
        $(ul).addClass('list-group');
        subject.topics.map(function(topic){
          topicList[topic.id] = topic.title.toUpperCase();
          var li = document.createElement("li");
          $(li).addClass('list-group-item');
          // li.innerHTML = topic.title;
          var checkbox_div = document.createElement("div");
          $(checkbox_div).addClass('form-check');
          // checkbox_div.innerHTML = topic.title;
          var checkbox = document.createElement("input");
          $(checkbox).addClass('form-check-input');
          $(checkbox).attr({
            type:"checkbox",
            id:topic.id,
            "topic-subject-id":subject.id,
            name:"topic"
            });
          $(checkbox_div).append(checkbox);
          var checkbox_label = document.createElement("label");
          $(checkbox_label).addClass("form-check-label");
          $(checkbox_label).html(topic.title)

          $(checkbox_div).append(checkbox_label);
          $(li).append(checkbox_div);
          $(ul).append(li)
        });
        $(topic_div).append(ul);
        $('#topics-row').append(topic_div);
      });
    } else {

      if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE){

        (new InfoModal("Nothing left at all!",'<p class="lead">Either there\'s no more unanswered questions left in the system, or you\'ve forgotten to set the topics to <b>Show</b></p><hr class="my-4"><p>You\'ll need to talk to the Admin.</p>')).show();

      } else if (activityObject.ActivityType === ACTIVITYTYPE.DOUBTS){

        (new InfoModal("Nice work!!",'<p class="lead">Seems there\'s no more doubts left for you to clarify.</p><hr class="my-4"><p>Why don\'t you answer some quesitons instead.</p>')).show();

      }
      
      $("#sign-in").hide();
      // clean up any previous stuff
      $('#subjects-row').empty();
      $('#topics-row').empty();
      $('#topic-chooser').hide();

    }

  }});
  

}



function input_change(){
  if ($('#email').val() === '' || $('#password').val() === ''){
    $("#signin").prop('disabled', true);
  }
  
  if ($('#email').val() !== '' && $('#password').val() !== ''){
    $("#signin").prop('disabled', false);
  }

  var validEmailFormat = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
  if (!$('#email').val().match(validEmailFormat)){
    $("#emailHelp").show().text("Invlaid email address format").addClass("badInput");
  }
}

function __setTodaysQuestions(result){
  let todaysQuestions = JSON.parse(result);
  let totalTimeTaken = 0;
  $(todaysQuestions).each(function(){
    totalTimeTaken += parseInt(this.timetaken);
  });
  let averageTimePerQuestion = totalTimeTaken/todaysQuestions.length;
  let mins = Math.floor(averageTimePerQuestion/60);
  let secs = Math.round(averageTimePerQuestion - mins*60);
  let timeToDisplay = '';
  if (todaysQuestions.length){
    if (mins){
      timeToDisplay = `@<b>${mins}:${secs}</b> mins/question`;
    } else {
      timeToDisplay = `@<b>${secs}</b> secs/question`;
    }
  }
  $('#today-question-counter').html(`Today: <b>${todaysQuestions.length}</b> question(s)${timeToDisplay}`).show();
}

function __addTests(result){
  let tests = JSON.parse(result);
  $(tests.jee).each(function(){
    $('<button>', {
      class:"list-group-item list-group-item-action",
      name:"test-starter",
      text:this.title,
      "test-id":this.id,
      "test-name":this.test_name,
    }).appendTo($('#jee-test-list'));
  });
  $(tests.cbse).each(function(){
    $('<button>', {
      class:"list-group-item list-group-item-action",
      name:"test-starter",
      text:this.title,
      "test-id":this.id
    }).appendTo($('#cbse-test-list'));
  });

}


function signinClick(){
  $('#emailHelp, #passwordHelp').hide();
  url = activityObject.Config.rest_api_base_url + 'validateuser/' + $('#email').val() + '/' + encodeURIComponent($('#password').val());
  $.ajax({url: url, success: function(result){
    studentObject = JSON.parse(result);    
    if (studentObject.isvaliduser){
      if (studentObject.updatesrequired){
        $("#sign-in").hide();
        $("#app-is-old").show();
        

      } else {
        let ajaxUrl = activityObject.Config.rest_api_base_url + 'questionsattemptedtoday/' + studentObject.id;
        $.ajax({url: ajaxUrl, success: function(questionsattemptedtodayresult){
          // we also need to get the test list
          let ajaxUrl = activityObject.Config.rest_api_base_url + 'gettestlist';
          $.ajax({url: ajaxUrl, success: function(result){            
            $("#sign-in").hide();
            $("#app-is-old").hide();
            $('#activity-chooser').show();
            $('#user-stuff').show();
            __setTodaysQuestions(questionsattemptedtodayresult);
            __addTests(result);
            $('#drop-down-menu-title').text(studentObject.firstname + " " + studentObject.lastname);
            $('#user-email').text(studentObject.email);
            $('#user-role').text(studentObject.role);
          }});
        }});
      }

      } else {
        if (studentObject.isvalidemail){
          $('#passwordHelp').show();
        } else{
          $('#emailHelp').show();
        }
      }
  }});
}

// using this to format the string, take any of the following and return it with the correct padding
function _getNiceTimeStr(timeUnit){
  return String(timeUnit).padStart(2,'0');
}

function filterTopicList(){
  let filterStr = $("#topic-filter-text").val().toUpperCase();
  // var result = topicList.filter((word, index) => );
  var result = topicList.map((word,index) => word.includes(filterStr) ? index : undefined)
  $("[name='topic']").each(function(){
    result[this.id] === undefined ? $("#" + this.id).closest('li').hide() : $("#" + this.id).closest('li').show()

  });

}

function __init_page_elements(){
  $("form").on("submit", function (e) {e.preventDefault();});
  $("#signin").prop('disabled', true);
  $("#email").trigger( "focus" );
  $('#emailHelp, #passwordHelp').hide();
  if ($(location).attr('href').includes("pcm")){
    $("[test-name='cbse']").hide();
    $("#cbse-tests").parent().hide();
    $("#page-title").text("JEE Test Questions");
    
  } else if  ($(location).attr('href').includes("cbse")){
    $("[test-name='jee']").hide();
    $("#jee-tests").parent().hide();
    $("#page-title").text("CBSE Test Questions");
  }
  $("#sign-in").show();
}

$(function(){
  $.getJSON( "includes/config.json", function( config ) {
    activityObject.Config = config;
    __init_page_elements();
    
    
    $('#email, #password').on({
      change: function(){
        input_change();
      }
    });

    $("#attempt-answer").on({
      click: function(){
        submitAnswer();
      }
    });



    $("[name=manage-doubts]").on({
      click: function(){
        let question = activityObject.AttemptedQuestion === null ? activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex] : activityObject.AttemptedQuestion;
        if (question.doubttype === null){ //new question
          $('#doubt-question-id').html(`<h3>${question.id}</h3>`);
          $("#save-for-doubt-description").text();
          (new Modal($('#save-for-doubt-modal'))).show();
        } else{
          var ajaxUrl = activityObject.Config.rest_api_base_url;
          ajaxUrl += `savefordoubt/${studentObject.id}/${question.id}/''`;
          $.ajax({url: ajaxUrl, success: function(result){
            let resultObj = JSON.parse(result);
            question.savefordoubt = resultObj.savefordoubt;
            $("[name=manage-doubts]").removeClass("disabled");
            if (resultObj.savefordoubt === "0"){
              $("[name=manage-doubts]").text("Save for doubt");
              question.doubttype = null;
            } else if (resultObj.savefordoubt === "1"){
              if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE || activityObject.ActivityType === ACTIVITYTYPE.TESTRESULT){
                $("[name=manage-doubts]").text("Saved!. Click to Undo");
              } else if (activityObject.ActivityType === ACTIVITYTYPE.DOUBTS){
                $('[name=manage-doubts]').text('Mark as doubt cleared');
              }
            } else if (resultObj.savefordoubt === "2"){
              if (activityObject.ActivityType === ACTIVITYTYPE.DOUBTS){
                $('[name=manage-doubts]').text('Doubt cleared');
                $("[name=manage-doubts]").addClass("disabled");
              }
            }
          
          }});          
        }

      }
    });

    // called from save-for-doubt-modal
    $("[name=save-for-doubt]").on({
      click: function(){
        $("[name=manage-doubts]").text("Saving doubt...");
        $("[name=manage-doubts]").addClass("disabled");
        let question = activityObject.AttemptedQuestion === null ? activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex] : activityObject.AttemptedQuestion;
        let ajaxUrl = activityObject.Config.rest_api_base_url;
        ajaxUrl += "savefordoubt";
        question.doubttype = $(this).attr('doubt-type');
        let studentattempted = { studentid: studentObject.id,
                                  questionid: question.id,
                                  doubttype: $(this).attr('doubt-type'),
                                  description:$("#save-for-doubt-description").val()
                                };
        $.post(ajaxUrl, JSON.stringify(studentattempted), function(result){
          $("[name=manage-doubts]").text("Saved!. Click to Undo");
          $("[name=manage-doubts]").removeClass("disabled");
        }); 
      }
    });


    $("[name=manage-notes]").on({
      click: function(){
        $("[name=manage-notes]").text("Saving. Please wait").addClass("disabled");
        var question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];
        var ajaxUrl = activityObject.Config.rest_api_base_url + "saveasnote/" + studentObject.id + "/" + question.id;
        $.ajax({url: ajaxUrl, success: function(result){
          $("[name=manage-notes]").text("Saved!");
        }});
      }
    });


    $("#submit-test").on({
      click: function(){
        submitTest();
      }
    });

    $("#force-submit-test").on({
      click: function(){
        activityObject.Test.EndModal.hide();
        submitTest(true);
      }
    });

    $("#continue-test").on({
      click: function(){
        activityObject.Test.ForceSubmit = false;
      }
    });


    $("[name=navigate-question]").on({
      click: function(){
        if (activityObject.ActivityType === ACTIVITYTYPE.TEST){
          storeStudentAttempt();
          setupTestQuestion(Number($(this).attr('direction')));
        } else if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE){
          setupQuestion(Number($(this).attr('direction')));
        } else if (activityObject.ActivityType === ACTIVITYTYPE.DOUBTS){
          setupDoubtOrNoteQuestion(Number($(this).attr('direction')));
        }  else if (activityObject.ActivityType === ACTIVITYTYPE.TESTRESULT){
          setupTestQuestion(Number($(this).attr('direction')));
        }
      }
    });    

    $("#topic-filter-text").on({
      keypress: function(event){
        if (event.key === "Enter"){
          filterTopicList();

        }
      }
    });

    $("#filter-topic-list").on({
      click: function(){
        filterTopicList();
      }
    });

    $("[name='choose-activity']").on({
      click: function(){
        activityObject.ActivityType = Number($(this).attr('activity-type'));
        activityObject.ActivityTitle = $(this).attr('activity-title');
        load_subjects_and_topics($(this).attr('test-name'));
      }
    })

    $("#start-activity").on({
      click: function(){
        startActivity();
      }
    });


    $("#get-latest-updates").on({
      click: function(){
        // http://localhost:8089/services/rest.api.php/updateapprefreshdata/2
        // 2023-09-24 15:14:48
        const today = new Date();
        let y = today.getFullYear();
        let M = _getNiceTimeStr(today.getMonth() + 1);
        let d = _getNiceTimeStr(today.getDate())
        let h = _getNiceTimeStr(today.getHours());
        let m = _getNiceTimeStr(today.getMinutes());
        let s = _getNiceTimeStr(today.getSeconds());
        let timeStr = y + "-" + M + "-" + d + " " + h + ":" + m + ":" + s
        let ajaxUrl = activityObject.Config.rest_api_base_url + 'updateapprefreshdata/' + studentObject.id + "/" + encodeURIComponent(timeStr);

        $.ajax({url: ajaxUrl, success: function(result){
          let retval = JSON.parse(result);
          window.location.href = window.location.href
          location.reload(true);
        }});        
      }
    });    


    $("#signin").on({
      click: function(){
        signinClick();
      }
    });



    $("[name=back-to-activity-chooser]").on({
      click: function(){
        $('#the-test').closest('main').removeClass('col-10').addClass('col-6');
        $('#the-test').hide();
        $('#topic-chooser').hide();
        $('#activity-chooser').show();
        activityObject.ActivityType = ACTIVITYTYPE.NONE;
        activityObject.ActivityTitle = null;
      }
    });
    $('[name=answer-details-button]').on({
      click: function(){
        let question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];
        addAnswerDetails(question);
        var myModal = new Modal($('#answer-details'));
        myModal.show();
      }
    });
    $("#back-to-topic-chooser").on({
      click: function(){
        $('#topic-chooser').show();
        $('#the-questionaire').hide();
        CurrentQuestionIndex : -1;
        $("[name='all-topic-selector']").each(function(){
          $(this).removeClass("btn-primary");
          $(this).addClass("btn-outline-primary");
  
          let topicCheckboxes = $("input[topic-subject-id*='" + $(this).attr("subject-id") + "']");
          $(topicCheckboxes).each(function(){
            $(this).prop( "checked", false );
          })
        });
                
        $("input[name*='topic']:checked").each(function(){
          $(this).prop( "checked", false );
        });
      }
    });

    // click of Start button on Start test modal
    $("#start-test").on({
      click: function(){
        startTest();
      }
    });

    $("#attempted-questions-modal").on({
      'hidden.bs.modal': function(){
        $('[name=manage-doubts][location=attempted-questions-modal]').hide();
        activityObject.AttemptedQuestion = null;
      }
    });


    $("#open-attempted-questions-modal").on({
      click: function(){
        $('[name=manage-doubts][location=attempted-questions-modal]').show().text("Save for doubt");
        var attemptedQuestionsModal = new Modal('#attempted-questions-modal');
        attemptedQuestionsModal.show();    
        // every time we open the Attempted Questions modal, let's reset the question counter
        activityObject.AttemptedQuestionIndex = 1;
        setupAttemptedQuestion();
      }
    });

    $("[name=navigate-attempted-question]").on({
      click: function(){
        activityObject.AttemptedQuestionIndex += parseInt($(this).attr('direction'));
        if (activityObject.AttemptedQuestionIndex === 1){
          $("[name=navigate-attempted-question][direction=-1]").prop("disabled",true);
        } else {
          $("[name=navigate-attempted-question][direction=-1]").prop("disabled",false);
        }
        setupAttemptedQuestion();
      }
    });    


    $("[name=bookmark-question]").on({
      click: function(){
        var question = activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex];
        if (question.bookmark){ //unbookmark
          question.bookmark = false;
          $(this).removeClass('btn-primary').addClass('btn-outline-primary').attr('title',"Bookmark this question");
        } else {
          question.bookmark = true;
          $(this).removeClass('btn-outline-primary').addClass('btn-primary').attr('title',"Remove question bookmark");
        }        
      }
    });

    $(document).on("click", "[name='all-topic-selector']", function(){
      let topicCheckboxes = $("input[topic-subject-id*='" + $(this).attr("subject-id") + "']");
      if ($(this).attr("selected-all") === "1"){
        topicCheckboxes.each(function(){
          $(this).prop( "checked", false );
        });
        $(this).removeClass("btn-primary");
        $(this).addClass("btn-outline-primary");
        $(this).attr("selected-all",0);
        

      } else {
        topicCheckboxes.each(function(){
          $(this).prop( "checked", true );
        });
        $(this).addClass("btn-primary");
        $(this).removeClass("btn-outline-primary");
        $(this).attr("selected-all",1);

      }
    });

    // click of test from test list
    $(document).on("click", "[name='test-starter']", function(){
      testStarter($(this).attr('test-id'),$(this).attr('test-name'),$(this).text());
    });

    $(document).on("click", "[id='pause-question']", function(){
      activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex].times.push(Date.now());
      (new Modal($('#pause-question-modal'))).show();
      $(this).removeClass('pause-question').addClass('play-question').html("&#9655;").attr("title","Play question");
    });

    $("[id=restart-question]").on({
      click: function(){
        $("#pause-question").removeClass('pause-question').addClass('play-question').html("&#9612;&#9612;").attr("title","Pause question");
        activityObject.CurrentSubject.questions[activityObject.CurrentSubject.CurrentQuestionIndex].times.push(Date.now());
      }
    });    


    // click of numbered list question (see question-number-list)
    $(document).on("click", "[name='number-list-item']", function(){
      storeStudentAttempt();
      setupTestQuestion(Direction.BYINDEX,Number($(this).attr("question-index")));
    });

    // for tests
    $(document).on("show.bs.tab", 'button[data-bs-toggle="pill"]', function(){
      if (activityObject.ActivityType === ACTIVITYTYPE.TEST || activityObject.ActivityType === ACTIVITYTYPE.TESTRESULT){
        storeStudentAttempt();
        activityObject.CurrentSubject = activityObject.Subjects[$(this).attr('subject-name')];
        setupTestQuestion(Direction.NONE);
      }
    });

    // for questionaires and doubts and notes
    $(document).on("show.bs.tab", 'button[data-bs-toggle="tab"]', function(){
      if (activityObject.ActivityType === ACTIVITYTYPE.QUESTIONAIRE){
        activityObject.CurrentSubject = activityObject.Subjects[$(this).attr('subject-name')];
        $('[name=navigate-question][direction="1"]').show();
        setupQuestion();
      } else {
        activityObject.CurrentSubject = activityObject.Subjects[$(this).attr('subject-name')];
        setupDoubtOrNoteQuestion();
      }
    });    
   
  });
});
