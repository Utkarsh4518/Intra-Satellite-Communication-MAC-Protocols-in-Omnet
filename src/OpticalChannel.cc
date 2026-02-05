#include <omnetpp.h>
using namespace omnetpp;

class OpticalChannel : public cSimpleModule {
  protected:
    int activeTx = 0;

    void handleMessage(cMessage *msg) override {
        if (msg->getKind() == 1) {
            activeTx++;
            if (activeTx > 1)
                msg->setKind(99);
            send(msg, "out", msg->getArrivalGate()->getIndex());
        }
        else if (msg->getKind() == 0) {
            activeTx--;
            delete msg;
        }
        else
            delete msg;
    }
};

Define_Module(OpticalChannel);
