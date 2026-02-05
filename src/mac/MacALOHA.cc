#include <omnetpp.h>
#include "MacBase.cc"

using namespace omnetpp;

class MacALOHA : public MacBase {
  private:
    cMessage *genEvent = nullptr;
    simtime_t currentPacketGenTime;
    int hopsCompleted = 0;

  protected:
    void initialize() override {
        genEvent = new cMessage("gen");
        scheduleAt(simTime() + uniform(0, 0.05), genEvent);
    }

    void handleMessage(cMessage *msg) override {
        if (msg == genEvent) {
            generated++;
            txAttempts++;
            currentPacketGenTime = simTime();
            hopsCompleted = 0;
            send(new cMessage("data", 1), "out");
            cancelAndDelete(genEvent);
            genEvent = nullptr;
            return;
        }

        if (strcmp(msg->getName(), "reTX") == 0 || strcmp(msg->getName(), "hop") == 0) {
            txAttempts++;
            send(new cMessage("data", 1), "out");
            delete msg;
            return;
        }

        send(new cMessage("end", 0), "out");

        if (msg->getKind() == 99) {
            collisions++;
            scheduleAt(simTime() + exponential(0.05), new cMessage("reTX"));
        } else {
            int numHops = (int)par("numHops");
            hopsCompleted++;
            if (hopsCompleted >= numHops) {
                recordDelivery(currentPacketGenTime);
                genEvent = new cMessage("gen");
                scheduleAt(simTime() + uniform(0, 0.05), genEvent);
            } else {
                scheduleAt(simTime() + uniform(0, 0.02), new cMessage("hop"));
            }
        }
        delete msg;
    }

    void finish() override {
        if (genEvent) cancelAndDelete(genEvent);
        MacBase::finish();
    }
};

Define_Module(MacALOHA);
