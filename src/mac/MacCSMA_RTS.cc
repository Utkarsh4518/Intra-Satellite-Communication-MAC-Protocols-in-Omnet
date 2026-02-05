#include <omnetpp.h>
#include "MacBase.cc"

using namespace omnetpp;

class MacCSMA_RTS : public MacBase {
  private:
    cMessage *genEvent = nullptr;
    simtime_t currentPacketGenTime;
    int hopsLeft = 0;

  protected:
    void initialize() override {
        genEvent = new cMessage("gen");
        scheduleAt(simTime() + uniform(0, 0.05), genEvent);
    }

    void handleMessage(cMessage *msg) override {
        if (msg == genEvent) {
            generated++;
            currentPacketGenTime = simTime();
            hopsLeft = (int)par("numHops");
            txAttempts++;
            send(new cMessage("RTS", 10), "out");
            scheduleAt(simTime() + 0.01, new cMessage("rts_hop"));
            cancelAndDelete(genEvent);
            genEvent = nullptr;
            return;
        }

        if (strcmp(msg->getName(), "rts_hop") == 0) {
            hopsLeft--;
            if (hopsLeft > 0) {
                txAttempts++;
                send(new cMessage("RTS", 10), "out");
                scheduleAt(simTime() + 0.01, new cMessage("rts_hop"));
            } else {
                recordDelivery(currentPacketGenTime);
                genEvent = new cMessage("gen");
                scheduleAt(simTime() + 0.05, genEvent);
            }
            delete msg;
            return;
        }

        if (msg->getKind() == 99) collisions++;
        delete msg;
    }

    void finish() override {
        if (genEvent) cancelAndDelete(genEvent);
        MacBase::finish();
    }
};

Define_Module(MacCSMA_RTS);
