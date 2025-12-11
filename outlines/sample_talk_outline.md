---
slide: 1
type: title              # title | section | content | image_only | transition
layout: title_slide      # PowerPoint-ish layout names
style: glass_garden:title
generate: true

title: Holistic generation of slide decks
subtitle: From assembling to rendering

text:
  bullets: []

visual: |
  Cinematic hero slide: glass/ceramic desk, soft volumetric light, translucent UI panels.
  Keep text minimal, focus on the hero scene. Left/right balance; centered title.

assets:
  - imgs/qrcode.png

notes: |
  Opening hook about how we currently make slides and where we're going.
---

---
slide: 2
type: content
layout: two_content                   # map to a two-column concept
style: glass_garden:default
generate: true

title: Background problem
subtitle: The old world

text:
  columns:
    - heading: Old
      bullets:
        - Fragmented visuals
        - Manual layout
        - Time sink
    - heading: New
      bullets:
        - Cohesive visuals
        - Minimal manual layout
        - Faster iteration

visual: |
  Two-column composition: left anchored by "Old" text and fragmented visuals; right anchored by "New" text and a cohesive rendered scene. Make the contrast obvious.

assets:
  - imgs/style_matrix_0.jpg

style_ref: []    # optional global/style reference image(s)

notes: |
  Explain the traditional slide-making pain: overworked layouts, visual clutter, time cost.
---

---
slide: 3
type: transition
layout: section_header
style: glass_garden:default
generate: true

title: From assembling to rendering

text:
  bullets: []

visual: |
  Abstract transition visual suggesting a shift from manual assembly to rendered coherence.
  Light, minimal, keeps the mood without heavy text.

assets: []
style_ref: []
notes: |
  Light connective slide; minimal or no embedded text.
---

---
slide: 4
type: image_only
layout: picture_with_caption          # image on one side, calmer space on the other
style: glass_garden:visual
generate: true

title: The Generative Kernel

text:
  bullets: []

visual: |
  Hero visual of the "Generative Kernel": nested glass spheres with light at the core,
  no visible labels except maybe a tiny tasteful mark. Bold, metaphoric, minimal text.

assets:
  - imgs/style_matrix_0.jpg

style_ref: []

notes: |
  Pure visual emphasis; no embedded text needed.
---
