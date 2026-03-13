import { describe, it, expect } from 'vitest'

/**
 * BubbleToolbar unit tests.
 *
 * The component depends heavily on TipTap's Editor instance and BubbleMenuPlugin,
 * which are difficult to mock in a jsdom environment. These tests verify the
 * structural expectations that can be validated without a live editor.
 */

describe('BubbleToolbar component contract', () => {
  it('module exports a default function component', async () => {
    const mod = await import('../BubbleToolbar')
    expect(typeof mod.default).toBe('function')
  })

  it('expected toolbar actions are defined in source', async () => {
    // Read the source to verify action labels are present
    // This is a lightweight structural test
    const source = await import('../BubbleToolbar?raw')
    const text = source.default

    const expectedLabels = [
      'Bold',
      'Italic',
      'Underline',
      'Strikethrough',
      'Inline Code',
      'Heading 1',
      'Heading 2',
      'Heading 3',
      'Bullet List',
      'Ordered List',
      'Blockquote',
      'Code Block',
      'Align Left',
      'Align Center',
      'Align Right',
      'Undo',
      'Redo',
      'Clear Formatting',
    ]

    for (const label of expectedLabels) {
      expect(text).toContain(label)
    }
  })

  it('includes link form UI elements', async () => {
    const source = await import('../BubbleToolbar?raw')
    const text = source.default

    expect(text).toContain('Link URL')
    expect(text).toContain('Apply')
    expect(text).toContain('Cancel')
    expect(text).toContain('https://…')
  })

  it('has proper ARIA attributes in source', async () => {
    const source = await import('../BubbleToolbar?raw')
    const text = source.default

    expect(text).toContain('role="toolbar"')
    expect(text).toContain('aria-label="Text formatting"')
    expect(text).toContain('role="menuitem"')
    expect(text).toContain('aria-pressed')
  })

  it('handles keyboard navigation with ArrowRight/ArrowLeft/Escape', async () => {
    const source = await import('../BubbleToolbar?raw')
    const text = source.default

    expect(text).toContain('ArrowRight')
    expect(text).toContain('ArrowLeft')
    expect(text).toContain('ArrowUp')
    expect(text).toContain('ArrowDown')
    expect(text).toContain('Escape')
  })
})
