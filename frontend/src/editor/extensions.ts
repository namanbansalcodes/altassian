import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TextAlign from '@tiptap/extension-text-align'
import { Extension, type Extensions } from '@tiptap/react'

/**
 * Custom extension that adds Ctrl/Cmd+K keyboard shortcut to toggle links.
 * When text is selected and has no link, prompts for a URL and sets the link.
 * When the cursor is on an existing link, removes it.
 */
const LinkKeyboardShortcut = Extension.create({
  name: 'linkKeyboardShortcut',

  addKeyboardShortcuts() {
    return {
      'Mod-k': ({ editor }) => {
        if (editor.isActive('link')) {
          editor.chain().focus().unsetLink().run()
          return true
        }
        const url = window.prompt('Enter URL:')
        if (url?.trim()) {
          editor.chain().focus().setLink({ href: url.trim() }).run()
        }
        return true
      },
    }
  },
})

export function getEditorExtensions(placeholder = 'Start writing...'): Extensions {
  return [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
    }),
    Placeholder.configure({ placeholder }),
    Underline,
    Link.configure({
      openOnClick: false,
      HTMLAttributes: { class: 'text-blue-600 underline cursor-pointer' },
    }),
    LinkKeyboardShortcut,
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({ resizable: true }),
    TableRow,
    TableCell,
    TableHeader,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
  ]
}
