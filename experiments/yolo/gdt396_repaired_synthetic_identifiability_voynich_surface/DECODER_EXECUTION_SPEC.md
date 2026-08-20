# GDT396 decoder execution split

Status: `FROZEN_BEFORE_DECODER_PANEL_AND_QUALIFICATION`.

The mechanical blind training blocks are:

- legacy seeds `0..19` train development decodes;
- legacy plus development train qualification decodes;
- legacy plus development plus qualification observations train confirmation
  decodes.

Each world and surface channel is fitted separately. No oracle row enters
decoder fitting. One model is fit per decoder/world/surface/phase and supplied
unchanged to each seed/representation decode; the runner hashes and checks
model immutability. No confirmation observation is used to fit another
confirmation seed.
