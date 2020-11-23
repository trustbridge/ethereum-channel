pragma solidity >=0.4.22 <0.7.0;
pragma experimental ABIEncoderV2;


contract ChannelNode {
    struct Participant {
        address participantAddress;
        ChannelNode participantContract;
    }

    mapping(string => Participant) public participants;
    string[] public participantList;
    address[] senderList;

    struct Message {
        string subject;
        string predicate;
        string obj;
        string sender;
        string receiver;
    }

    address public owner;
    // according to github issues of web3py, web3py decoder can't decode events that have structure as a parameter.
    event MessageReceivedEvent(
      string subject,
      string predicate,
      string obj,
      string sender,
      string receiver
    );
    event MessageSentEvent(
      string subject,
      string predicate,
      string obj,
      string sender,
      string receiver
    );

    constructor(string[] memory _participantList) public {
        owner = msg.sender;
        participantList = _participantList;
    }

    function getParticipants() public view returns (string[] memory) {
        return participantList;
    }

    function getParticipant(string memory participant) public view returns (Participant memory)
    {
        return participants[participant];
    }

    // FIXME: add or check that participant name in participantsList
    function addParticipant(
        string memory _name,
        address _address
    ) public {
        require(
            msg.sender == owner,
            "Only the owner of this contract can add participants."
        );
        participants[_name].participantAddress = _address;
    }

    function updateParticipantContractAddress(
        string memory _name,
        address _address
    ) public {
        require(
            msg.sender == participants[_name].participantAddress,
            "Only this participant can change their contract address."
        );
        participants[_name].participantContract = ChannelNode(_address);
    }

    function receiveMessage(Message memory message) public {
        emit MessageReceivedEvent(
          message.subject,
          message.predicate,
          message.obj,
          message.sender,
          message.receiver
        );
    }

    function send(Message memory message) public {
        Participant memory receiver = participants[message.receiver];

        require(receiver.participantAddress != address(0), "UserError: receiver not found");
        require(address(receiver.participantContract) != address(0), "UserError: receiver participant contract is not set");

        receiver.participantContract.receiveMessage(message);

        emit MessageSentEvent(
          message.subject,
          message.predicate,
          message.obj,
          message.sender,
          message.receiver
        );
    }
}
