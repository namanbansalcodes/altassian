import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEditor, EditorContent } from '@tiptap/react'
import {
  Bold, Italic, Underline as UnderlineIcon, Heading1, Heading2, Heading3,
  List, ListOrdered, Code, Quote, Minus, Undo, Redo, Save,
  AlignLeft, AlignCenter, AlignRight, CheckSquare, Link as LinkIcon,
} from 'lucide-react'
import * as api from '../api'
import { toast, getErrorMessage } from '../lib/toast'
import { getEditorExtensions } from '../editor/extensions'
import BubbleToolbar from '../components/BubbleToolbar'
import SlashMenu from '../components/SlashMenu'
import { EditorSkeleton } from '../components/Skeleton'

function ToolbarButton({ onClick, active, children, title }: { onClick: () => void; active?: boolean; children: React.ReactNode; title?: string }) {
  return (
    <button type="button" onClick={onClick} title={title} data-compact-touch
      className={`p-2 sm:p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 ${active ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'text-gray-600 dark:text-gray-400'}`}>
      {children}
    </button>
  )
}

function Divider() {
  return <div className="w-px h-5 bg-gray-300 dark:bg-gray-600 mx-1" />
}

export default function PageEditor() {
  const { spaceKey, pageSlug } = useParams<{ spaceKey: string; pageSlug: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isEditing = !!pageSlug

  const { data: existingPage, isLoading: pageLoading } = useQuery({
    queryKey: ['page', spaceKey, pageSlug],
    queryFn: () => api.getPage(spaceKey!, pageSlug!),
    enabled: isEditing,
  })

  const [title, setTitle] = useState('')

  const editor = useEditor({
    extensions: getEditorExtensions(),
    content: '',
    editorProps: {
      attributes: {
        class: 'prose prose-blue dark:prose-invert max-w-none min-h-[200px] sm:min-h-[300px] md:min-h-[400px] outline-none p-4 sm:p-6 prose-responsive',
      },
    },
  })

  useEffect(() => {
    if (existingPage) {
      setTitle(existingPage.title)
      editor?.commands.setContent(existingPage.content || '')
    }
  }, [existingPage, editor])

  // Autosave: debounced save when editing an existing page
  const autosaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const autosaving = useRef(false)

  const autosave = useCallback(async () => {
    if (!isEditing || !editor || !title.trim() || autosaving.current) return
    autosaving.current = true
    try {
      await api.updatePage(spaceKey!, pageSlug!, { title, content: editor.getHTML() })
      toast.info('Autosaved', { duration: 1500 })
      queryClient.invalidateQueries({ queryKey: ['page'] })
    } catch {
      // Silent — manual save still available
    } finally {
      autosaving.current = false
    }
  }, [isEditing, editor, title, spaceKey, pageSlug, queryClient])

  useEffect(() => {
    if (!isEditing || !editor) return
    const handler = () => {
      if (autosaveTimer.current) clearTimeout(autosaveTimer.current)
      autosaveTimer.current = setTimeout(autosave, 30_000)
    }
    editor.on('update', handler)
    return () => {
      editor.off('update', handler)
      if (autosaveTimer.current) clearTimeout(autosaveTimer.current)
    }
  }, [isEditing, editor, autosave])

  const saveMut = useMutation({
    mutationFn: async () => {
      const content = editor?.getHTML() || ''
      if (isEditing) {
        return api.updatePage(spaceKey!, pageSlug!, { title, content })
      } else {
        return api.createPage(spaceKey!, { title, content })
      }
    },
    onSuccess: (page) => {
      queryClient.invalidateQueries({ queryKey: ['pages'] })
      queryClient.invalidateQueries({ queryKey: ['page'] })
      toast.success(isEditing ? 'Page updated' : 'Page created')
      navigate(`/spaces/${spaceKey}/pages/${page.slug}`)
    },
    onError: (err) => {
      toast.error(getErrorMessage(err))
    },
  })

  if (isEditing && pageLoading) return <EditorSkeleton />
  if (!editor) return null

  return (
    <div className="max-w-4xl mx-auto">
      <div className="editor-actions-sticky flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2 bg-gray-50 dark:bg-gray-950">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">{isEditing ? 'Edit Page' : 'New Page'}</h2>
        <div className="flex gap-2 w-full sm:w-auto">
          <button onClick={() => navigate(-1)}
            className="flex-1 sm:flex-initial px-3 sm:px-4 py-2.5 sm:py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-800 text-center">
            Cancel
          </button>
          <button onClick={() => saveMut.mutate()} disabled={!title.trim() || saveMut.isPending}
            className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-3 sm:px-4 py-2.5 sm:py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
            <Save size={14} /> {saveMut.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        {/* Title */}
        <input
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="Page title"
          className="w-full px-4 sm:px-6 py-3.5 sm:py-4 text-xl sm:text-2xl font-bold border-b border-gray-200 dark:border-gray-700 outline-none placeholder-gray-300 dark:placeholder-gray-600 bg-transparent text-gray-900 dark:text-gray-100"
        />

        {/* Static Toolbar */}
        <div className="relative border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-0.5 px-3 sm:px-4 py-2 bg-gray-50 dark:bg-gray-800 overflow-x-auto flex-nowrap sm:flex-wrap scrollbar-thin">
          <ToolbarButton onClick={() => editor.chain().focus().toggleBold().run()} active={editor.isActive('bold')} title="Bold (Ctrl+B)">
            <Bold size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleItalic().run()} active={editor.isActive('italic')} title="Italic (Ctrl+I)">
            <Italic size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive('underline')} title="Underline (Ctrl+U)">
            <UnderlineIcon size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleCode().run()} active={editor.isActive('code')} title="Inline Code (Ctrl+E)">
            <Code size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => {
            const url = window.prompt('Enter URL:')
            if (url) editor.chain().focus().setLink({ href: url }).run()
          }} active={editor.isActive('link')} title="Link (Ctrl+K)">
            <LinkIcon size={16} />
          </ToolbarButton>
          <Divider />
          <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} active={editor.isActive('heading', { level: 1 })} title="Heading 1">
            <Heading1 size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} active={editor.isActive('heading', { level: 2 })} title="Heading 2">
            <Heading2 size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()} active={editor.isActive('heading', { level: 3 })} title="Heading 3">
            <Heading3 size={16} />
          </ToolbarButton>
          <Divider />
          <ToolbarButton onClick={() => editor.chain().focus().toggleBulletList().run()} active={editor.isActive('bulletList')} title="Bullet List">
            <List size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleOrderedList().run()} active={editor.isActive('orderedList')} title="Ordered List">
            <ListOrdered size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleTaskList().run()} active={editor.isActive('taskList')} title="Task List">
            <CheckSquare size={16} />
          </ToolbarButton>
          <Divider />
          <ToolbarButton onClick={() => editor.chain().focus().toggleCodeBlock().run()} active={editor.isActive('codeBlock')} title="Code Block">
            <Code size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleBlockquote().run()} active={editor.isActive('blockquote')} title="Quote">
            <Quote size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().setHorizontalRule().run()} title="Divider">
            <Minus size={16} />
          </ToolbarButton>
          <Divider />
          <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('left').run()} active={editor.isActive({ textAlign: 'left' })} title="Align Left">
            <AlignLeft size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('center').run()} active={editor.isActive({ textAlign: 'center' })} title="Align Center">
            <AlignCenter size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('right').run()} active={editor.isActive({ textAlign: 'right' })} title="Align Right">
            <AlignRight size={16} />
          </ToolbarButton>
          <Divider />
          <ToolbarButton onClick={() => editor.chain().focus().undo().run()} title="Undo (Ctrl+Z)">
            <Undo size={16} />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().redo().run()} title="Redo (Ctrl+Shift+Z)">
            <Redo size={16} />
          </ToolbarButton>
        </div>
        {/* Scroll fade hint — visible only on mobile when toolbar overflows */}
        <div className="absolute right-0 top-0 bottom-0 w-6 bg-gradient-to-l from-gray-50 dark:from-gray-800 to-transparent pointer-events-none sm:hidden" />
        </div>

        {/* Editor with overlays */}
        <div className="relative">
          <EditorContent editor={editor} />
          <BubbleToolbar editor={editor} />
          <SlashMenu editor={editor} />
        </div>
      </div>

      {/* Error is shown via toast */}
    </div>
  )
}
