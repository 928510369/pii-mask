import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from '../App';

const mockUploadDocument = vi.fn();
const mockMaskPII = vi.fn();
const mockHealthCheck = vi.fn();

vi.mock('../api', () => ({
  uploadDocument: (...args: unknown[]) => mockUploadDocument(...args),
  maskPII: (...args: unknown[]) => mockMaskPII(...args),
  healthCheck: (...args: unknown[]) => mockHealthCheck(...args),
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe('App Component - Rendering', () => {
  it('renders the Alta-Lex branding', () => {
    render(<App />);
    expect(screen.getByText('Alta-Lex')).toBeInTheDocument();
    expect(screen.getByText('PII Shield')).toBeInTheDocument();
  });

  it('renders input and output panels', () => {
    render(<App />);
    expect(screen.getByText('Input')).toBeInTheDocument();
    expect(screen.getByText('Masked Output')).toBeInTheDocument();
  });

  it('renders the textarea with placeholder', () => {
    render(<App />);
    const textarea = screen.getByPlaceholderText(/Paste or type text/i);
    expect(textarea).toBeInTheDocument();
  });

  it('renders default PII categories', () => {
    render(<App />);
    expect(screen.getByText(/Name/)).toBeInTheDocument();
    expect(screen.getByText(/Phone/)).toBeInTheDocument();
    expect(screen.getByText(/Email/)).toBeInTheDocument();
    expect(screen.getByText(/Address/)).toBeInTheDocument();
    expect(screen.getByText(/ID Number/)).toBeInTheDocument();
    expect(screen.getByText(/Bank Card/)).toBeInTheDocument();
    expect(screen.getByText(/Social Media/)).toBeInTheDocument();
  });

  it('renders upload zone with accepted formats', () => {
    render(<App />);
    expect(screen.getByText('TXT, PDF, DOCX, CSV, XLSX')).toBeInTheDocument();
  });

  it('renders empty state in output panel', () => {
    render(<App />);
    expect(screen.getByText('Masked output will appear here')).toBeInTheDocument();
  });

  it('renders footer with Alta-Lex link', () => {
    render(<App />);
    const link = screen.getByText('Alta-Lex AI');
    expect(link).toHaveAttribute('href', 'https://www.alta-lex.ai/');
  });

  it('shows Qwen3-0.6B status', () => {
    render(<App />);
    expect(screen.getByText('Qwen3-0.6B Online')).toBeInTheDocument();
  });

  it('renders file upload area', () => {
    render(<App />);
    expect(screen.getByText('Drop a file here or click to upload')).toBeInTheDocument();
  });

  it('has custom category input', () => {
    render(<App />);
    expect(screen.getByPlaceholderText('Add custom category...')).toBeInTheDocument();
    expect(screen.getByText('+ Add')).toBeInTheDocument();
  });
});

describe('Text Input', () => {
  it('disables Mask PII button when textarea is empty', () => {
    render(<App />);
    const button = screen.getByRole('button', { name: /Mask PII/i });
    expect(button).toBeDisabled();
  });

  it('enables Mask PII button when text is entered', () => {
    render(<App />);
    const textarea = screen.getByPlaceholderText(/Paste or type text/i);
    fireEvent.change(textarea, { target: { value: 'Some text' } });
    const button = screen.getByRole('button', { name: /Mask PII/i });
    expect(button).not.toBeDisabled();
  });

  it('updates textarea value on input', () => {
    render(<App />);
    const textarea = screen.getByPlaceholderText(/Paste or type text/i) as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: 'Hello world' } });
    expect(textarea.value).toBe('Hello world');
  });

  it('clears text properly', () => {
    render(<App />);
    const textarea = screen.getByPlaceholderText(/Paste or type text/i) as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: 'Some text' } });
    expect(textarea.value).toBe('Some text');
    fireEvent.change(textarea, { target: { value: '' } });
    expect(textarea.value).toBe('');
  });
});

describe('File Upload', () => {
  it('shows file name after upload', async () => {
    mockUploadDocument.mockResolvedValue('Extracted text from file');
    render(<App />);

    const file = new File(['file content'], 'test.txt', { type: 'text/plain' });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/test\.txt/)).toBeInTheDocument();
    });
  });

  it('populates textarea after file upload', async () => {
    mockUploadDocument.mockResolvedValue('Extracted text from file');
    render(<App />);

    const file = new File(['file content'], 'test.txt', { type: 'text/plain' });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/Paste or type text/i) as HTMLTextAreaElement;
      expect(textarea.value).toBe('Extracted text from file');
    });
  });

  it('calls uploadDocument API on file input', async () => {
    mockUploadDocument.mockResolvedValue('Extracted text');
    render(<App />);

    const file = new File(['content'], 'doc.pdf', { type: 'application/pdf' });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(mockUploadDocument).toHaveBeenCalledWith(file);
    });
  });

  it('shows remove button when file is uploaded', async () => {
    mockUploadDocument.mockResolvedValue('text');
    render(<App />);

    const file = new File(['content'], 'report.docx', { type: 'application/docx' });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('✕')).toBeInTheDocument();
    });
  });

  it('removes file and clears text on remove button click', async () => {
    mockUploadDocument.mockResolvedValue('File text content');
    render(<App />);

    const file = new File(['content'], 'test.txt', { type: 'text/plain' });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/test\.txt/)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('✕'));

    expect(screen.queryByText(/test\.txt/)).not.toBeInTheDocument();
    const textarea = screen.getByPlaceholderText(/Paste or type text/i) as HTMLTextAreaElement;
    expect(textarea.value).toBe('');
  });

  it('shows error on upload failure', async () => {
    mockUploadDocument.mockRejectedValue(new Error('Upload failed'));
    render(<App />);

    const file = new File(['content'], 'bad.xyz', { type: 'text/plain' });
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/Upload failed/)).toBeInTheDocument();
    });
  });

  it('handles drag and drop', async () => {
    mockUploadDocument.mockResolvedValue('Dropped file text');
    render(<App />);

    const uploadZone = screen.getByText('Drop a file here or click to upload').closest('.upload-zone')!;
    const file = new File(['content'], 'dropped.txt', { type: 'text/plain' });

    fireEvent.dragOver(uploadZone, { preventDefault: () => {} });
    fireEvent.drop(uploadZone, {
      preventDefault: () => {},
      dataTransfer: { files: [file] },
    });

    await waitFor(() => {
      expect(mockUploadDocument).toHaveBeenCalledWith(file);
    });
  });
});

describe('PII Categories', () => {
  it('toggles a category off when clicked', async () => {
    const user = userEvent.setup();
    render(<App />);

    const nameCategory = screen.getByText(/Name/).closest('.category-tag')!;
    expect(nameCategory).toHaveClass('active');

    await user.click(nameCategory);
    expect(nameCategory).toHaveClass('inactive');
  });

  it('toggles a category back on', async () => {
    const user = userEvent.setup();
    render(<App />);

    const nameCategory = screen.getByText(/Name/).closest('.category-tag')!;
    await user.click(nameCategory); // off
    expect(nameCategory).toHaveClass('inactive');
    await user.click(nameCategory); // on again
    expect(nameCategory).toHaveClass('active');
  });

  it('adds a custom category', async () => {
    const user = userEvent.setup();
    render(<App />);

    const input = screen.getByPlaceholderText('Add custom category...');
    const addBtn = screen.getByText('+ Add');

    await user.type(input, 'passport');
    await user.click(addBtn);

    expect(screen.getByText(/passport/i)).toBeInTheDocument();
  });

  it('adds custom category on Enter key', async () => {
    const user = userEvent.setup();
    render(<App />);

    const input = screen.getByPlaceholderText('Add custom category...');
    await user.type(input, 'ssn{enter}');

    expect(screen.getByText(/ssn/i)).toBeInTheDocument();
  });

  it('does not add empty custom category', async () => {
    const user = userEvent.setup();
    render(<App />);

    const addBtn = screen.getByText('+ Add');
    const categoriesBefore = screen.getAllByText(/./i).filter(el =>
      el.classList.contains('category-tag')
    ).length;

    await user.click(addBtn);

    const categoriesAfter = screen.getAllByText(/./i).filter(el =>
      el.classList.contains('category-tag')
    ).length;

    expect(categoriesAfter).toBe(categoriesBefore);
  });

  it('does not add duplicate category', async () => {
    const user = userEvent.setup();
    render(<App />);

    const input = screen.getByPlaceholderText('Add custom category...');
    await user.type(input, 'name');
    await user.click(screen.getByText('+ Add'));

    // "name" category already exists; should not duplicate
    const nameElements = screen.getAllByText(/Name/);
    expect(nameElements.length).toBe(1);
  });

  it('shows active category count', () => {
    render(<App />);
    expect(screen.getByText(/7 active/)).toBeInTheDocument();
  });
});

describe('API Integration - Mask PII', () => {
  it('calls maskPII API when button clicked', async () => {
    mockMaskPII.mockResolvedValue({
      masked_text: 'Hello ████',
      detections: [{ type: 'name', original: 'John', start: 6, end: 10 }],
    });
    render(<App />);

    const textarea = screen.getByPlaceholderText(/Paste or type text/i);
    fireEvent.change(textarea, { target: { value: 'Hello John' } });

    const button = screen.getByRole('button', { name: /Mask PII/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockMaskPII).toHaveBeenCalledWith(
        'Hello John',
        expect.arrayContaining(['name', 'phone', 'email', 'address'])
      );
    });
  });

  it('displays masked output after API call', async () => {
    mockMaskPII.mockResolvedValue({
      masked_text: 'My name is ████ and email is ████',
      detections: [
        { type: 'name', original: 'John', start: 11, end: 15 },
        { type: 'email', original: 'john@test.com', start: 29, end: 42 },
      ],
    });
    render(<App />);

    const textarea = screen.getByPlaceholderText(/Paste or type text/i);
    fireEvent.change(textarea, { target: { value: 'My name is John and email is john@test.com' } });

    fireEvent.click(screen.getByRole('button', { name: /Mask PII/i }));

    await waitFor(() => {
      // masked blocks should be present in the output
      const maskedBlocks = document.querySelectorAll('.masked-block');
      expect(maskedBlocks.length).toBe(2);
      // output text container should exist
      const outputText = document.querySelector('.output-text');
      expect(outputText).not.toBeNull();
      expect(outputText!.textContent).toContain('My name is');
    });
  });

  it('shows detection summary badges', async () => {
    mockMaskPII.mockResolvedValue({
      masked_text: '████ called ████',
      detections: [
        { type: 'name', original: 'Alice', start: 0, end: 5 },
        { type: 'name', original: 'Bob', start: 13, end: 16 },
      ],
    });
    render(<App />);

    fireEvent.change(screen.getByPlaceholderText(/Paste or type text/i), {
      target: { value: 'Alice called Bob' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Mask PII/i }));

    await waitFor(() => {
      const badge = screen.getByText('name');
      expect(badge).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  it('shows loading state while processing', async () => {
    // Make the mock return a promise that we control
    let resolvePromise: (value: unknown) => void;
    mockMaskPII.mockImplementation(
      () => new Promise((resolve) => { resolvePromise = resolve; })
    );
    render(<App />);

    fireEvent.change(screen.getByPlaceholderText(/Paste or type text/i), {
      target: { value: 'Test text' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Mask PII/i }));

    await waitFor(() => {
      expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    });

    // Resolve to clean up
    resolvePromise!({
      masked_text: 'Test text',
      detections: [],
    });

    await waitFor(() => {
      expect(screen.queryByText('Analyzing...')).not.toBeInTheDocument();
    });
  });

  it('shows error on mask API failure', async () => {
    mockMaskPII.mockRejectedValue(new Error('API connection failed'));
    render(<App />);

    fireEvent.change(screen.getByPlaceholderText(/Paste or type text/i), {
      target: { value: 'Some PII text' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Mask PII/i }));

    await waitFor(() => {
      expect(screen.getByText(/API connection failed/)).toBeInTheDocument();
    });
  });

  it('sends only active categories to API', async () => {
    const user = userEvent.setup();
    mockMaskPII.mockResolvedValue({
      masked_text: 'test',
      detections: [],
    });
    render(<App />);

    // Toggle off Name and Phone
    const nameTag = screen.getByText(/Name/).closest('.category-tag')!;
    const phoneTag = screen.getByText(/Phone/).closest('.category-tag')!;
    await user.click(nameTag);
    await user.click(phoneTag);

    const textarea = screen.getByPlaceholderText(/Paste or type text/i);
    fireEvent.change(textarea, { target: { value: 'Test' } });
    fireEvent.click(screen.getByRole('button', { name: /Mask PII/i }));

    await waitFor(() => {
      expect(mockMaskPII).toHaveBeenCalled();
      const callArgs = mockMaskPII.mock.calls[0];
      expect(callArgs[1]).not.toContain('name');
      expect(callArgs[1]).not.toContain('phone');
      expect(callArgs[1]).toContain('email');
    });
  });
});

describe('Output Display', () => {
  it('shows Copy button when output exists', async () => {
    mockMaskPII.mockResolvedValue({
      masked_text: 'Hello ████',
      detections: [{ type: 'name', original: 'World', start: 6, end: 11 }],
    });
    render(<App />);

    // Initially no copy button
    expect(screen.queryByText(/Copy/)).not.toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText(/Paste or type text/i), {
      target: { value: 'Hello World' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Mask PII/i }));

    await waitFor(() => {
      expect(screen.getByText(/Copy/)).toBeInTheDocument();
    });
  });

  it('renders masked blocks with correct styling class', async () => {
    mockMaskPII.mockResolvedValue({
      masked_text: 'Contact ████ at ████',
      detections: [
        { type: 'name', original: 'Alice', start: 8, end: 13 },
        { type: 'email', original: 'a@b.c', start: 17, end: 22 },
      ],
    });
    render(<App />);

    fireEvent.change(screen.getByPlaceholderText(/Paste or type text/i), {
      target: { value: 'Contact Alice at a@b.c' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Mask PII/i }));

    await waitFor(() => {
      const blocks = document.querySelectorAll('.masked-block');
      expect(blocks.length).toBe(2);
      blocks.forEach((block) => {
        expect(block.textContent).toBe('████');
      });
    });
  });
});
