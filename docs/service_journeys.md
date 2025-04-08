
# Service Journey
Service journeys provide the digital infrastructure for a customer to be able to modify information that is already stored in the `EIS` (enterprise information system) of Way2Wealth.
Currently the EIS in consideration is **TechXL**

## What can a customer modify ?
Here is the list of information that the customer can ask to be modified
### KYC Category
The following information falls under the category of KYC and are relevant to all the `holders`

> TODO
> Check if this list is exhaustive or anything else needs to be added

- Mobile Number
- Email Address
- Identity information
	- Name might change for various reasons
- Address information
	- Both residential and the correspondence address can change
- Wet signature
- Financial information
	- Income 
	- FATCA

### Account Information
The client may chose to change information that is related to the `Demat` account and also the `Trading` account

> TODO
> Is there anything else that is not part of the AOF that has to be part of the service journey ?

- Bank account
	- The client may chose to add and remove bank accounts
	- Mark bank account that has to be treated as the default
- Nomination Details
- Instructions to the trading account
	- > Need to get more details on this
- Standing instructions from the client

## Assumptions
The following are some assumptions that are made in designing the service request forms

1. In any service request form, KYC of **only one** of the holders will be modified
2. The customer will have the option of picking (upfront) what information needs to be changed
	1. The choice can be as granular as the business needs
3. If there is account with more than 1 holder and if the information that has to change is common to the holders, the change has to be effected in multiple requests
	1. Example 1
		1. Husband and Wife jointly hold an account. The correspondence address changes as they shift residence. The address has to be changed for both the holders.
		2. In such as case two service request has to be raised, one for each holder