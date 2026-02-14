# Edge Case Document

## Empty Section

## Section After Empty

This section follows an empty one with no content between headers.

## Adjacent Headers Test

### First Sub

### Second Sub

### Third Sub

These three subsections appear with no content between them except this text in the third.

## Code Block with Fake Headers

This section has headers inside a fenced code block that should NOT trigger splits:

```markdown
## This Is Not a Real Header

### Neither Is This

#### Nor This One
```

The chunker must ignore those lines above.

## Ünïcödé Séctïon 日本語

Content with special characters: café, naïve, résumé, über, straße.

Mathematical symbols: α β γ δ ε ζ η θ.

CJK characters: 你好世界 こんにちは 안녕하세요.

## Deeply Nested

### Level Three

#### Level Four

Content at level four with deep nesting to test hierarchy depth.

## Section with Only a List

- Item one
- Item two
- Item three

## Section with Only Code

```python
def hello():
    print("world")
```

## Final Section

This is the last section, testing that the final buffer is flushed correctly.
