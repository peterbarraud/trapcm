<?php
require_once ('datalayer.php');
class objectbase {
    public function __construct($id=null) {
        $this->id = $id;
        $dataLayer = DataLayer::Instance();
        $dataLayer->GetObjectData($this);
    }
    public function Save(){
        $dataLayer = DataLayer::Instance();
        $dataLayer->Save($this);
    }
    public function Delete()
    {
        $dataLayer = DataLayer::Instance();
        $affected_rows = $dataLayer->Delete($this);
        return $affected_rows;
    }
    public function __toString() {
        ob_start();
        var_dump($this);
        return ob_get_clean(); 
    }
}

?>