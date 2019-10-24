# WDMOC
The Whole Disease Model of Oral Cancer

Author: Ian Cromwell, PhD

Technical Advisor: Stavros Korokithakis (Stochastic Technologies)

Supervisory Committee: Dr. Nick Bansback, Dr. Catherine Poh, Dr. Stuart Peacock, Dr. Greg Werker, Dr. Charlyn Black

The Whole Disease Model of Oral Cancer (WDMOC) is a decision model developed for Health Technology Assessment (HTA), Health Technology Management (HTM) and cost-effectiveness analysis (CEA). A full description of the model is available under Documentation in the document entitled 'Methods.pdf', but a brief description follows.

The WDMOC is an individual sampling discrete event simulation (DES) model. Entities (simulated people) are created and given characteristics based on user-defined parameters (InputParameters.xlsx). These entities experience events using a time-to-event process. Randomly-sampled values of the input paramters determine each entity's path through various simulated health care processes - screening, management of preclinical lesions, management of invasive and recurring cancers, follow-up, and death. Resource utilization, survival, and health state utility (EQ-5D 3L) are tracked for each entity, along with a history of events experienced. At the end of each entity's simulated trajectory (either at death or a user-defined point), unit costs are applied to resources and overall and quality-adjusted survival are calculated. The user may simulate any number of entities. User-defined results from a cohort of simulated entities can be exported to a .csv file, which can then be analyzed in any software packge the user wishes. The model's structure is described in detail in 'Methods.pdf'.

The WDMOC is built in Python 3.5.1. To simulate a cohort of entities, run 'Sequencer.py'. The user may specify the number of simulated entities on **Line 106**.

I would like to acknowledge Kelly Liu for creating the retrospective cohort upon which the model parameters are based, and Dr. Huiying Sun who provided crucial statistical guidance. The creation of the WDMOC was partially funded by the pan-Canadian Centre for Applied Research in Cancer Control (ARCC), and many aspects of the work that went into this thesis reflect the input from my colleagues there.
