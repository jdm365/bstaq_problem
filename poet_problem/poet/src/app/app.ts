import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

import { PoetryService } from './poetry';

interface Poem {
  title: string;
  author: string;
  lines: string[];
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule
  ],
  templateUrl: './app.html',
  styleUrl: './app.css',
  providers: [PoetryService]
})
export class App implements OnInit {
  protected readonly title = signal('poet');

  authorPoems: Poem[] = [];
  authorSearchError: string | null = null;
  currentAuthorSearch: string = '';

  titlePoems: Poem[] = [];
  titleSearchError: string | null = null;
  currentTitleSearch: string = '';

  authorTitlePoems: Poem[] = [];
  authorTitleSearchError: string | null = null;
  currentAuthorTitleSearch: { author: string, title: string } = { author: '', title: '' };


  constructor(private poetryService: PoetryService) { }

  ngOnInit(): void {}

  searchAuthor(author: string): void {
    this.authorPoems = [];
    this.authorSearchError = null;
    this.currentAuthorSearch = author;

    if (!author) {
      this.authorSearchError = 'Enter an author name.';
      return;
    }

    this.poetryService.getPoemsByAuthor(author).subscribe({
      next: (poems) => {
        this.authorPoems = poems;
        if (poems.length === 0) {
          this.authorSearchError = `No poems found for author: "${author}"`;
        }
      },
      error: (err) => {
        console.error('Error fetching poems by author:', err);
        this.authorSearchError = `Failed to fetch poems: ${err.message || 'Unknown error'}`;
      }
    });
  }

  searchTitle(title: string): void {
    this.titlePoems = [];
    this.titleSearchError = null;
    this.currentTitleSearch = title;

    if (!title) {
      this.titleSearchError = 'Enter a title.';
      return;
    }

    this.poetryService.getPoemsByTitle(title).subscribe({
      next: (poems) => {
        this.titlePoems = poems;
        if (poems.length === 0) {
          this.titleSearchError = `No poems found with title: "${title}"`;
        }
      },
      error: (err) => {
        console.error('Error fetching poems by title:', err);
        this.titleSearchError = `Failed to fetch poems: ${err.message || 'Unknown error'}`;
      }
    });
  }

  searchAuthorAndTitle(author: string, title: string): void {
    this.authorTitlePoems = [];
    this.authorTitleSearchError = null;
    this.currentAuthorTitleSearch = { author, title };

    if (!author || !title) {
      this.authorTitleSearchError = 'Enter both author and title.';
      return;
    }

    this.poetryService.getPoemsByAuthorAndTitle(author, title).subscribe({
      next: (poems) => {
        this.authorTitlePoems = poems;
        if (poems.length === 0) {
          this.authorTitleSearchError = `No poems found by "${author}" with title "${title}"`;
        }
      },
      error: (err) => {
        console.error('Error fetching poems by author and title:', err);
        this.authorTitleSearchError = `Failed to fetch poems: ${err.message || 'Unknown error'}`;
      }
    });
  }
}
