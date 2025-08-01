import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

interface Poem {
  title: string;
  author: string;
  lines: string[];
}

@Injectable()
export class PoetryService {
  private baseUrl = 'https://poetrydb.org';

  constructor(private http: HttpClient) { }

  private handleError(error: HttpErrorResponse): Observable<never> {
    if (error.status === 0) {
      console.error('An client-side or network error occurred:', error.error);
    } else {
      console.error(
        `Backend returned code ${error.status}, body was: `, error.error);
    }
    return throwError(() => new Error('Something bad happened; please try again later.'));
  }

  getPoemsByAuthor(author: string): Observable<Poem[]> {
    const url = `${this.baseUrl}/author/${author}`;
    return this.http.get<Poem[]>(url).pipe(
      catchError(this.handleError),
      map(response => {
        if (response && Array.isArray(response)) {
          return response;
        } else {
          throw new Error(`No poems found for author: ${author}`);
        }
      })
    );
  }

  getPoemsByTitle(title: string): Observable<Poem[]> {
    const url = `${this.baseUrl}/title/${title}`;
    return this.http.get<Poem[]>(url).pipe(
      catchError(this.handleError),
      map(response => {
        if (response && Array.isArray(response)) {
          return response;
        } else {
          throw new Error(`No poems found with title: ${title}`);
        }
      })
    );
  }

  getPoemsByAuthorAndTitle(author: string, title: string): Observable<Poem[]> {
    const url = `${this.baseUrl}/author,title/${author};${title}`;
    return this.http.get<Poem[]>(url).pipe(
      catchError(this.handleError),
      map(response => {
        if (response && Array.isArray(response)) {
          return response;
        } else {
          throw new Error(`No poems found by author "${author}" with title "${title}"`);
        }
      })
    );
  }
}
