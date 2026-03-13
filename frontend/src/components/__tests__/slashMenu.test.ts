import { describe, it, expect } from 'vitest'
import { filterCommands, slashCommands } from '../SlashMenu'

describe('filterCommands', () => {
  it('returns all commands when query is empty', () => {
    expect(filterCommands('')).toEqual(slashCommands)
  })

  it('filters by label match', () => {
    const results = filterCommands('heading')
    expect(results.length).toBeGreaterThanOrEqual(3)
    expect(results.every((c) => c.label.toLowerCase().includes('heading'))).toBe(true)
  })

  it('filters by keyword match', () => {
    const results = filterCommands('h1')
    expect(results.length).toBe(1)
    expect(results[0].id).toBe('heading1')
  })

  it('filters by description match', () => {
    const results = filterCommands('checklist')
    expect(results.length).toBe(1)
    expect(results[0].id).toBe('taskList')
  })

  it('is case insensitive', () => {
    const results = filterCommands('BULLET')
    expect(results.some((c) => c.id === 'bulletList')).toBe(true)
  })

  it('returns empty array for no matches', () => {
    const results = filterCommands('zzzznocommandhere')
    expect(results).toEqual([])
  })

  it('finds table by keyword "grid"', () => {
    const results = filterCommands('grid')
    expect(results.length).toBe(1)
    expect(results[0].id).toBe('table')
  })

  it('finds divider by keyword "hr"', () => {
    const results = filterCommands('hr')
    expect(results.length).toBe(1)
    expect(results[0].id).toBe('divider')
  })

  it('partial match works for keywords', () => {
    const results = filterCommands('code')
    expect(results.some((c) => c.id === 'codeBlock')).toBe(true)
  })

  it('all commands have required fields', () => {
    for (const cmd of slashCommands) {
      expect(cmd.id).toBeTruthy()
      expect(cmd.label).toBeTruthy()
      expect(cmd.description).toBeTruthy()
      expect(typeof cmd.execute).toBe('function')
      expect(cmd.keywords.length).toBeGreaterThan(0)
    }
  })

  it('finds page link by keyword "page"', () => {
    const results = filterCommands('page')
    expect(results.some((c) => c.id === 'pageLink')).toBe(true)
  })

  it('finds page link by keyword "wiki"', () => {
    const results = filterCommands('wiki')
    expect(results.length).toBe(1)
    expect(results[0].id).toBe('pageLink')
  })

  it('includes pageLink command in full list', () => {
    expect(slashCommands.some((c) => c.id === 'pageLink')).toBe(true)
  })

  it('finds task list by keyword "todo"', () => {
    const results = filterCommands('todo')
    expect(results.length).toBe(1)
    expect(results[0].id).toBe('taskList')
  })
})
