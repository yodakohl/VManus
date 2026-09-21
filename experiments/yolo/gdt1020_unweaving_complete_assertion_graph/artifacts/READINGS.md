# Complete conditional assertion readings
All values are unconfirmed. P12projection only; two diplomatic forms remain unbound.

## DIRECT

Habitual phase assignments: {"UNRAVEL": "NIGHT", "WEAVE": "DAY"}.

|Clause|All written groups|Construction|Created assertion frames|Resolved references|
|---|---|---|---|---|
|C1|`qokeedy qolchey qokeey qokedy`|ACTION_PAIR|||
|C2|`chedy otal`|PREREQUISITE|||
|C3|`otchey qokeey qoky`|SECRET_HABIT|E1||
|C4|`tol shedy qokylddy`|PUBLIC_PLEDGE|E2|P1|
|C5|`dain chedy qokeedy shckhedy shckhedy`|UNTIL_HABIT|E3||
|C6|`saiin cheeky sheey qokedy shedy oldy`|RESPECTIVE_TIMES||A1,E3,E1|
|C7|`salchedy cheey qody kesd oldy`|REPORT_DISCOVERY|E4,E5|E1|
|C8|`s okeedy qokeedy qoky saii`|THEN_COMPLETE|E6|E5,T1|

Computed complete assertion graph:

```json
{
  "cloth": "CURRENT_CLOTH",
  "worker": "WOMAN",
  "audience": "WOOERS",
  "action_pairs": [
    {
      "id": "A1",
      "actions": [
        "WEAVE",
        "UNRAVEL"
      ],
      "cloth": "CURRENT_CLOTH"
    }
  ],
  "prerequisites": [
    {
      "id": "P1",
      "predicate": "FINISHED",
      "cloth": "CURRENT_CLOTH",
      "social_act": "MARRIAGE",
      "worker": "WOMAN",
      "asserted": false
    }
  ],
  "endpoints": [
    {
      "id": "T1",
      "predicate": "FINISHED",
      "action": "WEAVE",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "prospective": true
    }
  ],
  "events": [
    {
      "id": "E1",
      "kind": "HABIT",
      "clause": "C3",
      "action": "UNRAVEL",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "period": "PRIOR",
      "phase": "NIGHT",
      "concealed": true,
      "audience": "WOOERS"
    },
    {
      "id": "E2",
      "kind": "PLEDGE",
      "clause": "C4",
      "worker": "WOMAN",
      "audience": "WOOERS",
      "content": "P1",
      "period": "PRIOR",
      "phase": "DAY"
    },
    {
      "id": "E3",
      "kind": "HABIT",
      "clause": "C5",
      "action": "WEAVE",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "period": "PRIOR",
      "phase": "DAY",
      "concealed": false,
      "endpoint": "T1",
      "distribution": {
        "kind": "DISTRIBUTIVE",
        "unit": "ROW_OF_WOVEN_WORK",
        "written_repetitions": 2
      }
    },
    {
      "id": "E4",
      "kind": "INFORM",
      "clause": "C7",
      "speaker": "HANDMAID",
      "audience": "WOOERS",
      "content": "E1"
    },
    {
      "id": "E5",
      "kind": "DISCOVER",
      "clause": "C7",
      "subject": "WOOERS",
      "content": "E1",
      "phase": "NIGHT",
      "knowledge": true
    },
    {
      "id": "E6",
      "kind": "BOUNDED_ACTION",
      "clause": "C8",
      "action": "WEAVE",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "compulsion": "UNDER_COMPULSION",
      "endpoint": "T1",
      "asserted_state": {
        "predicate": "FINISHED",
        "cloth": "CURRENT_CLOTH"
      },
      "phase": null
    }
  ],
  "temporal_edges": [
    [
      "E4",
      "E5",
      false
    ],
    [
      "E1",
      "E5",
      true
    ],
    [
      "E2",
      "E5",
      true
    ],
    [
      "E3",
      "E5",
      true
    ],
    [
      "E5",
      "E6",
      true
    ]
  ],
  "temporal_witness": {
    "E1": 0,
    "E2": 0,
    "E3": 0,
    "E4": 0,
    "E5": 1,
    "E6": 2
  },
  "knowledge": [
    {
      "content": "E1",
      "audience": "WOOERS",
      "before_discovery": false
    },
    {
      "content": "E1",
      "audience": "WOOERS",
      "at": "E5",
      "known": true
    }
  ],
  "trace": [
    {
      "clause": "C1",
      "kind": "ACTION_PAIR",
      "start": 0,
      "end": 4,
      "new_events": [],
      "references": []
    },
    {
      "clause": "C2",
      "kind": "PREREQUISITE",
      "start": 4,
      "end": 6,
      "new_events": [],
      "references": []
    },
    {
      "clause": "C3",
      "kind": "SECRET_HABIT",
      "start": 6,
      "end": 9,
      "new_events": [
        "E1"
      ],
      "references": []
    },
    {
      "clause": "C4",
      "kind": "PUBLIC_PLEDGE",
      "start": 9,
      "end": 12,
      "new_events": [
        "E2"
      ],
      "references": [
        "P1"
      ]
    },
    {
      "clause": "C5",
      "kind": "UNTIL_HABIT",
      "start": 12,
      "end": 17,
      "new_events": [
        "E3"
      ],
      "references": []
    },
    {
      "clause": "C6",
      "kind": "RESPECTIVE_TIMES",
      "start": 17,
      "end": 23,
      "new_events": [],
      "references": [
        "A1",
        "E3",
        "E1"
      ]
    },
    {
      "clause": "C7",
      "kind": "REPORT_DISCOVERY",
      "start": 23,
      "end": 28,
      "new_events": [
        "E4",
        "E5"
      ],
      "references": [
        "E1"
      ]
    },
    {
      "clause": "C8",
      "kind": "THEN_COMPLETE",
      "start": 28,
      "end": 33,
      "new_events": [
        "E6"
      ],
      "references": [
        "E5",
        "T1"
      ]
    }
  ]
}
```

## REVERSED

Habitual phase assignments: {"UNRAVEL": "DAY", "WEAVE": "NIGHT"}.

|Clause|All written groups|Construction|Created assertion frames|Resolved references|
|---|---|---|---|---|
|C1|`qokeedy qolchey qokeey qokedy`|ACTION_PAIR|||
|C2|`chedy otal`|PREREQUISITE|||
|C3|`otchey qokeey qoky`|SECRET_HABIT|E1||
|C4|`tol shedy qokylddy`|PUBLIC_PLEDGE|E2|P1|
|C5|`dain chedy qokeedy shckhedy shckhedy`|UNTIL_HABIT|E3||
|C6|`saiin cheeky sheey qokedy shedy oldy`|RESPECTIVE_TIMES||A1,E3,E1|
|C7|`salchedy cheey qody kesd oldy`|REPORT_DISCOVERY|E4,E5|E1|
|C8|`s okeedy qokeedy qoky saii`|THEN_COMPLETE|E6|E5,T1|

Computed complete assertion graph:

```json
{
  "cloth": "CURRENT_CLOTH",
  "worker": "WOMAN",
  "audience": "WOOERS",
  "action_pairs": [
    {
      "id": "A1",
      "actions": [
        "WEAVE",
        "UNRAVEL"
      ],
      "cloth": "CURRENT_CLOTH"
    }
  ],
  "prerequisites": [
    {
      "id": "P1",
      "predicate": "FINISHED",
      "cloth": "CURRENT_CLOTH",
      "social_act": "MARRIAGE",
      "worker": "WOMAN",
      "asserted": false
    }
  ],
  "endpoints": [
    {
      "id": "T1",
      "predicate": "FINISHED",
      "action": "WEAVE",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "prospective": true
    }
  ],
  "events": [
    {
      "id": "E1",
      "kind": "HABIT",
      "clause": "C3",
      "action": "UNRAVEL",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "period": "PRIOR",
      "phase": "DAY",
      "concealed": true,
      "audience": "WOOERS"
    },
    {
      "id": "E2",
      "kind": "PLEDGE",
      "clause": "C4",
      "worker": "WOMAN",
      "audience": "WOOERS",
      "content": "P1",
      "period": "PRIOR",
      "phase": "DAY"
    },
    {
      "id": "E3",
      "kind": "HABIT",
      "clause": "C5",
      "action": "WEAVE",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "period": "PRIOR",
      "phase": "NIGHT",
      "concealed": false,
      "endpoint": "T1",
      "distribution": {
        "kind": "DISTRIBUTIVE",
        "unit": "ROW_OF_WOVEN_WORK",
        "written_repetitions": 2
      }
    },
    {
      "id": "E4",
      "kind": "INFORM",
      "clause": "C7",
      "speaker": "HANDMAID",
      "audience": "WOOERS",
      "content": "E1"
    },
    {
      "id": "E5",
      "kind": "DISCOVER",
      "clause": "C7",
      "subject": "WOOERS",
      "content": "E1",
      "phase": "NIGHT",
      "knowledge": true
    },
    {
      "id": "E6",
      "kind": "BOUNDED_ACTION",
      "clause": "C8",
      "action": "WEAVE",
      "worker": "WOMAN",
      "cloth": "CURRENT_CLOTH",
      "compulsion": "UNDER_COMPULSION",
      "endpoint": "T1",
      "asserted_state": {
        "predicate": "FINISHED",
        "cloth": "CURRENT_CLOTH"
      },
      "phase": null
    }
  ],
  "temporal_edges": [
    [
      "E4",
      "E5",
      false
    ],
    [
      "E1",
      "E5",
      true
    ],
    [
      "E2",
      "E5",
      true
    ],
    [
      "E3",
      "E5",
      true
    ],
    [
      "E5",
      "E6",
      true
    ]
  ],
  "temporal_witness": {
    "E1": 0,
    "E2": 0,
    "E3": 0,
    "E4": 0,
    "E5": 1,
    "E6": 2
  },
  "knowledge": [
    {
      "content": "E1",
      "audience": "WOOERS",
      "before_discovery": false
    },
    {
      "content": "E1",
      "audience": "WOOERS",
      "at": "E5",
      "known": true
    }
  ],
  "trace": [
    {
      "clause": "C1",
      "kind": "ACTION_PAIR",
      "start": 0,
      "end": 4,
      "new_events": [],
      "references": []
    },
    {
      "clause": "C2",
      "kind": "PREREQUISITE",
      "start": 4,
      "end": 6,
      "new_events": [],
      "references": []
    },
    {
      "clause": "C3",
      "kind": "SECRET_HABIT",
      "start": 6,
      "end": 9,
      "new_events": [
        "E1"
      ],
      "references": []
    },
    {
      "clause": "C4",
      "kind": "PUBLIC_PLEDGE",
      "start": 9,
      "end": 12,
      "new_events": [
        "E2"
      ],
      "references": [
        "P1"
      ]
    },
    {
      "clause": "C5",
      "kind": "UNTIL_HABIT",
      "start": 12,
      "end": 17,
      "new_events": [
        "E3"
      ],
      "references": []
    },
    {
      "clause": "C6",
      "kind": "RESPECTIVE_TIMES",
      "start": 17,
      "end": 23,
      "new_events": [],
      "references": [
        "A1",
        "E3",
        "E1"
      ]
    },
    {
      "clause": "C7",
      "kind": "REPORT_DISCOVERY",
      "start": 23,
      "end": 28,
      "new_events": [
        "E4",
        "E5"
      ],
      "references": [
        "E1"
      ]
    },
    {
      "clause": "C8",
      "kind": "THEN_COMPLETE",
      "start": 28,
      "end": 33,
      "new_events": [
        "E6"
      ],
      "references": [
        "E5",
        "T1"
      ]
    }
  ]
}
```
