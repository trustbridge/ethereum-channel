pragma solidity >=0.4.21 <0.7.0;

contract EventEmitter {
  
  uint public eventsCount = 0;
  
  event EventOne(string message);
  event EventTwo(string message);
  event EventThree(string message);
  event EventFour(string message);
  
  constructor() public {}
  
  function emitEvent(uint id, string memory message) public returns (bool) {
    if(id == 1){
      emit EventOne(message);
      eventsCount += 1;
      return true;
    } else if (id == 2){
      emit EventTwo(message);
      eventsCount += 1;
      return true;
    }else if (id == 3){
      emit EventThree(message);
      eventsCount += 1;
      return true;
    }else if (id == 4){
      emit EventFour(message);
      eventsCount += 1;
      return true;
    }
    return false;
  }
}
