# CafeMatrix
CafeMatrix is a fusion of objective / subjective coffee shop rankings, visualized in 3d space. More details on https://ethan-cope.github.io/.
Each axis of the 3d graph represents a criteria by which the coffee shop is ranked, called an *index*. The three indices are:
- ambiance (decor, crowdedness)
- value for money (cost, taste)
- study suitability (internet, seating)
Indices are ranked from 1-10, and are calculated from *sub-indices*. Sub-indices are specific attributes of the cafe, ranked from 1-5. Each index has 3 sub-indices.

## Indices

### [AMBIANCE INDEX]
ambiance sub-indices:
- [VIBE] - SUBJECTIVE ranking of decor / vibe from 0-5. 
- [SEATING AVAILABILITY] - SEMI-SUBJECTIVE. How difficult was it to find seats? 0-5.
- [SPARK] - SUBJECTIVE. Was there anything special not captured in the previous category? Nice baristas? fun games? Becomes a bar at night / open mic night? Activities / active part of community?  rank here, from 0-5. 

### [VALUE INDEX]
value sub-indices:
- [TASTE] - SUBJECTIVE ranking of how good the coffee was. 
- [COST] - SEMI-OBJECTIVE price of a cup of drip coffee here. 
- [MENU / SPARK] - SUBJECTIVE ranking of specials, or quality. Do they roast or sell their own beans? Have cool specials? Good food / cocktails also? all that goes here. 

### [STUDY INDEX]
study suitability sub-indices
- [SPACE SUITABILITY] - SUBJECTIVE. whether the existing space is good suitable for studying.
0-5 (not many spaces - normal - tons of space) 
- [TECH-FRIENDLINESS] - SEMI-OBJECTIVE ranking of internet functionality and outlet availability. 
0-5, (spotty / nonfunctional internet - fine internet) ditto for outlets
- [ACCESSIBILITY] - SEMI-OBJECTIVE ranking of how late / early it's open, and what days. 
Is it close to highways / public transit / easy to get to? Is parking good? 0-5. (hard to reach / bad hours - great hours / convenient location)

## Development Creative Backlog
- scaling determined by (tsv file OR frontend)? - you can change it if you so desire
- add location / support for multiple matrices in different locations.
- add ssl


