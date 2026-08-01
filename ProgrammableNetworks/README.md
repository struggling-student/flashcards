# Programmable Networks oral-exam flashcards

The flashcards are grouped by source lecture. Each `##` heading is one oral-exam prompt and the content that follows is its answer, as required by `markdown-anki-decks`.

The deck also contains **100 curated slide visuals** attached to the answers where diagrams materially improve understanding or recall. The images cover protocol stacks, packet formats, architecture blocks, forwarding pipelines, placement constraints, service-chain flows, SRv6 packet transformations, and P4 processing. Applied cards additionally use responsive tables and syntax-highlighted NETCONF XML, YANG, YAML, P4-like code, command, and pseudocode blocks.

| Markdown deck | Source material | Cards |
| --- | --- | ---: |
| `001-course-introduction.md` | Course introduction and motivation | 4 |
| `002-networking-basics.md` | Networking basics | 17 |
| `003-netconf-yang.md` | NETCONF, SNMP, and YANG | 37 |
| `004-sdn-openflow.md` | SDN and OpenFlow | 23 |
| `005-nfv-use-cases.md` | NFV use cases | 19 |
| `006-nfv-architecture.md` | NFV architecture and orchestration | 19 |
| `007-vnf-placement.md` | VNF placement | 13 |
| `008-service-function-chaining.md` | Service Function Chaining | 19 |
| `009-segment-routing.md` | Segment Routing and SRv6 | 28 |
| `010-programmable-data-plane.md` | Programmable data plane | 20 |
| `011-p4-ecosystem.md` | P4 and P4Runtime | 23 |
| **Total** | **11 lecture groups** | **222** |

Administrative information such as contact details and timetables was read during the source review but intentionally excluded from the study cards. Technical definitions, architectures, comparisons, algorithms, workflows, and diagram-driven examples are included.

## Generate the Anki packages

From the repository root:

```bash
python3 -m pip install -r ProgrammableNetworks/requirements-anki.txt
python3 ProgrammableNetworks/build_visuals.py
mkdir -p ProgrammableNetworks/anki
mdankideck ProgrammableNetworks/flashcards ProgrammableNetworks/anki \
  --prefix "Programmable Networks::"

# Optional: create one package containing all 11 subdecks.
python3 ProgrammableNetworks/build_anki.py
```

`build_visuals.py` renders the selected PDF slides as uniquely named JPEG files directly beside the Markdown decks. This layout intentionally follows the media-path and filename limitations of `markdown-anki-decks` and Anki.

The `click<8.2` pin avoids an incompatibility between the current Click release and the Typer version required by `markdown-anki-decks` 1.1.1. Pygments supplies syntax highlighting for the fenced code examples.

Import `ProgrammableNetworks/anki/programmable-networks.apkg` to add the entire course in one operation. The per-lecture `.apkg` files are also available for selective import. In both cases, the prefix makes the lectures subdecks of the `Programmable Networks` root deck.
