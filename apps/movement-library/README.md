# XF Movement Library

A snappy recall-first UI for expert-sourced movement cards. The goal is to answer: "I know I should move, but what exactly should I do right now?"

## Run

```bash
cd apps/movement-library
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Product shape

- Movement cards, not long videos
- Three cues max per card
- Use-when, dose, common miss, retest, and source on every card
- Context filters: desk, pre-WOD, post-WOD, TV/passive, dad-safe, travel
- Protocol shelf for tiny flows
- No rabbit holes in the default experience

## Next data step

Move the seeded card data into Markdown frontmatter under `references/mobility/movements/`, then generate the app data from those cards.
