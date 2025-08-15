<?php
    class NameValue{
        public function __construct($name, $operator, $value) {
            $this->name = $name;
            $this->operator = $operator;
            $this->value = $value;
        }
        public function Name(){return "$this->name";}
        public function Operator(){return $this->operator;}
        public function Value(){return $this->value;}
        public function __toString() {
            return $this->value; 
        }
    
    }
?>